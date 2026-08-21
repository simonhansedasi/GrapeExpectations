#!/usr/bin/env python3
"""
Coffee berry borer generation capacity under warming, from a degree-day model.

Hamilton et al. 2019 (PLoS ONE 14:e0218321) publish both a generations-versus-
elevation regression and the degree-day parameters behind it. The regression is
the wrong instrument here: it is fitted over 204-778 m, so reading a warming
response off it means extrapolating past its upper sampling limit, and it uses
elevation as a proxy for the temperature this analysis already has directly.

This applies their degree-day estimate to temperature instead -- 332 DD per
generation above a lower threshold of 14.9 C, both from that paper -- and first
checks that doing so reproduces the field rates they observed.

Run from the repo root:  python ML/07_cbb_degree_days.py
"""
import json
import os

LTT = 14.9        # C, lower developmental threshold (Hamilton et al. 2019)
DD_PER_GEN = 332  # degree-days, infestation to mature F1 (Hamilton et al. 2019)
SLOPE, ICPT = -5.721, 23.834   # within-belt lapse and intercept (notebook E6.1)
SEASON_DAYS = 184.0            # ~July-December berry availability window
DT = {"2035": 1.00, "2045": 1.35}

temp = lambda z: ICPT + SLOPE * z / 1000.0
gen_per_month = lambda z, dt=0.0: 30.4 * (temp(z) + dt - LTT) / DD_PER_GEN
gen_per_season = lambda z, dt=0.0: SEASON_DAYS * (temp(z) + dt - LTT) / DD_PER_GEN

N = {"cbb_dd_ltt": float(LTT), "cbb_dd_per_gen": float(DD_PER_GEN)}

print("check: degree-day model against Hamilton's observed 0.33-0.78 gen/month")
for z in (204, 300, 500, 700, 778):
    print(f"  {z:4d} m  T={temp(z):5.2f} C  {gen_per_month(z):.2f} gen/mo"
          f"   their regression {-0.0008 * z + 0.95:.2f}")
N["cbb_dd_gen_month_204"] = gen_per_month(204)
N["cbb_dd_gen_month_778"] = gen_per_month(778)
print(f"  600-780 m season total {gen_per_season(780):.2f}-{gen_per_season(600):.2f}"
      f"  (they report 2.11-3.27)")

print("\nwarming response (proportional, = dT / (T - LTT); independent of DD_PER_GEN)")
for z in (600, 800):
    for h, dt in DT.items():
        pct = dt / (temp(z) - LTT) * 100
        N[f"cbb_dd_{z}_{h}_pct"] = float(pct)
        print(f"  {z} m {h}: +{pct:4.1f}%   "
              f"{gen_per_season(z):.2f} -> {gen_per_season(z, dt):.2f} gen/season")

pn = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "paper_numbers.json")
d = json.load(open(pn)); d.update(N); json.dump(d, open(pn, "w"), indent=1)
print(f"\nmerged {len(N)} keys into paper_numbers.json")

if __name__ == "__main__":
    # the model must land inside the range Hamilton actually observed, or the
    # parameters have been transcribed wrong
    assert 0.33 <= gen_per_month(778) <= 0.78, gen_per_month(778)
    assert 0.33 <= gen_per_month(204) <= 0.78, gen_per_month(204)
    assert 2.11 <= gen_per_season(780) <= 3.27, gen_per_season(780)
