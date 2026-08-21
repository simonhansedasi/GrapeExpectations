#!/usr/bin/env python3
"""Parse HCA cupping PDFs (5 different layouts) into one table.

Column ORDER varies by year but district/variety/processing are closed vocabularies,
so match those anywhere in the line and take the leading text as the farm name.
"""
import re, subprocess, sys, unicodedata
import pandas as pd

YEARS = [2019, 2021, 2022, 2023, 2024]

DISTRICT = {
    'kona': 'Kona', "ka'u": "Ka'u", 'kau': "Ka'u", 'maui': 'Maui',
    "o'ahu": 'Oahu', 'oahu': 'Oahu', 'hamakua': 'Hamakua', 'hilo': 'Hilo',
    'puna': 'Puna', "kaua'i": 'Kauai', 'kauai': 'Kauai',
    "hawai'i": 'HawaiiOther', 'hawaii': 'HawaiiOther',
}
# order matters: longest / most specific first
PROC = [('fruit', 'natural'), ('natural', 'natural'), ('parchment', 'washed'),
        ('fully washed', 'washed'), ('washed', 'washed'), ('pulp', 'honey'),
        ('honey', 'honey')]
VAR = [('gesha', 'Geisha'), ('geisha', 'Geisha'), ('pacamara', 'Pacamara'),
       ('bourbon', 'Bourbon'), ('catuai', 'Catuai'), ('caturra', 'Caturra'),
       ('typica', 'Typica'), ('mokka', 'Mokka'), ('mocca', 'Mokka'),
       ('sl34', 'SL34'), ('sl-34', 'SL34'), ('k7', 'K7'), ('progeny', 'Progeny'),
       ('maragog', 'Maragogype')]

def norm(s):
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return s.replace('‘', "'").replace('’', "'").replace('ʻ', "'")

def pick(low, table):
    for key, val in table:
        if key in low:
            return val
    return None

rows = []
for y in YEARS:
    txt = subprocess.run(['pdftotext', '-layout', f'r{y}.pdf', '-'],
                         capture_output=True, text=True).stdout
    for line in txt.split('\n'):
        line = norm(line)
        low = line.lower()
        # a score is 8x.xx or 9x.x -- reject rank numbers and years
        m = re.findall(r'\b([789]\d\.\d{1,3})\b', line)
        if not m:
            continue
        score = float(m[-1] if y == 2022 else m[0])   # 2022 puts score last
        dist = None
        for key, val in DISTRICT.items():
            if re.search(r'\b' + re.escape(key) + r'\b', low):
                dist = val
                break
        if dist is None:
            continue
        # farm = leading text after stripping a leading rank/score number
        head = re.sub(r'^\s*\d+\s+', '', line)
        head = re.sub(r'^\s*[789]\d\.\d{1,3}\s*', '', head)
        farm = re.split(r'\s{2,}', head.strip())[0].strip()
        if len(farm) < 3:
            continue
        rows.append(dict(year=y, score=score, farm=farm, district=dist,
                         processing=pick(low, PROC), variety=pick(low, VAR)))

df = pd.DataFrame(rows).drop_duplicates()
df.to_csv('hca_scores.csv', index=False)
print(f"parsed {len(df)} rows across {df.year.nunique()} years")
print(df.groupby(['year', 'district']).size().unstack(fill_value=0))
print(f"\nscore range {df.score.min():.2f}-{df.score.max():.2f}")
print(f"variety known {df.variety.notna().mean():.0%}, processing known {df.processing.notna().mean():.0%}")
KAU = "Ka'u"
big = df[df.district.isin(['Kona', KAU])]
kona, kau = big[big.district == 'Kona'], big[big.district == KAU]
print(f"\nBig Island coffee-district rows: {len(big)}  (Kona {len(kona)}, Ka'u {len(kau)})")
print(f"distinct farms: Kona {kona.farm.nunique()}, Ka'u {kau.farm.nunique()}")
print("\nmost-entered Kona farms (these are the ones worth geocoding):")
print(kona.farm.value_counts().head(20).to_string())
print("\nmost-entered Ka'u farms:")
print(kau.farm.value_counts().head(10).to_string())
