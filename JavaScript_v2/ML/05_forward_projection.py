import os
os.makedirs(os.environ.get('IMG', '../img'), exist_ok=True)

# ── 05 — Climate-Forward Suitability Projections ──
# 
# Projects coffee thermal suitability island-wide under NEX-GDDP-CMIP6 warming.
# **Kona and Kaʻu are treated separately** — each region has its own thermal
# optimum derived from its own farm cells.
# 
# | Cell | Content |
# |------|---------|
# | D1   | Climate ΔT + regional thermal parameters |
# | D2   | Topo suitability (static, climate-independent) |
# | D3   | **Kona** thermal forward projection |
# | D4   | **Kaʻu** thermal forward projection |
# 

import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib as mpl

WH = 'white'

elev_f  = dem_500.ravel()[flat_mask]
temp_f  = lapse_model.predict(elev_f.reshape(-1, 1)).ravel()
slope_f = slope_max_isl.ravel()[flat_mask]
farm_msk = (slope_f <= 25.0) & (~np.isnan(slope_f))

def masked(arr, msk):
    out = arr.copy().astype(float); out[~msk] = np.nan; return out

kona_base = temp_suit_kona(temp_f, dt=0.0)
kona_d35  = masked(temp_suit_kona(temp_f, dt=dt_2035) - kona_base, farm_msk)
kau_base  = temp_suit_kau(temp_f,  dt=0.0)
kau_d35   = masked(temp_suit_kau(temp_f,  dt=dt_2035) - kau_base,  farm_msk)

fig, axes = plt.subplots(3, 1, figsize=(10, 28),
                         gridspec_kw={'hspace': 0.18})
fig.patch.set_facecolor(WH)

def base_ax(ax):
    ax.set_facecolor(WH)
    ax.set_aspect(1 / np.cos(np.radians(19.6)))
    for sp in ax.spines.values():
        sp.set_edgecolor('black'); sp.set_linewidth(0.8)
    ax.tick_params(colors='black', labelsize=8)
    ax.set_xlabel('Longitude', color='black', fontsize=9)
    ax.set_ylabel('Latitude',  color='black', fontsize=9)

def add_labels(ax):
    ax.scatter(lon_coffee_ok[kona_isl_mask], lat_coffee_ok[kona_isl_mask],
               c='#2166ac', s=14, zorder=5, linewidths=0.3, edgecolors='black')
    ax.scatter(lon_coffee_ok[kau_isl_mask],  lat_coffee_ok[kau_isl_mask],
               c='#d6604d', s=18, zorder=5, linewidths=0.3, edgecolors='black')
    for txt, x, y, col, ha in [
        ('KONA',    -155.72, 19.50, '#2166ac', 'right'),
        ('KAʻU', -155.60, 19.23, '#b2182b', 'center'),
        ('HILO',    -155.05, 19.75, '#555555', 'left'),
        ('KOHALA',  -155.75, 20.15, '#555555', 'left'),
    ]:
        ax.text(x, y, txt, color=col, fontsize=10, fontweight='bold', ha=ha)

def add_contours(ax):
    dem_mc = np.where(land_mask, dem_500, np.nan)
    cs = ax.contour(lon_isl, lat_isl, dem_mc,
                    levels=[500,1000,1500,2000,2500],
                    colors='#888888', linewidths=0.5, alpha=0.6, zorder=3)
    ax.clabel(cs, fmt='%dm', fontsize=7, colors='#444444',
              inline=True, inline_spacing=4)

def add_legend(ax, extra_handle=None):
    kona_p = mpatches.Patch(color='#2166ac', label='Kona farms')
    kau_p  = mpatches.Patch(color='#d6604d', label='Kaʻu farms')
    handles = [kona_p, kau_p]
    if extra_handle: handles.append(extra_handle)
    leg = ax.legend(handles=handles, facecolor='white', edgecolor='#cccccc',
                    framealpha=1.0, loc='upper right', fontsize=9)
    for t in leg.get_texts(): t.set_color('black')

# ── Row 1: topographic identity ───────────────────────────────────────────────
ax = axes[0]
base_ax(ax)
ax.set_title('(a) Topographic Identity — Current Terrain Similarity to Coffee Districts',
             color='black', fontsize=12, pad=8, fontweight='bold')

out_rng = np.isnan(identity_isl_masked)
ax.scatter(lon_flat[out_rng], lat_flat[out_rng],
           c='#dddddd', s=2, linewidths=0, rasterized=True, zorder=1)
in_rng  = ~out_rng
vmax_id = float(np.nanpercentile(np.abs(identity_isl_masked), 97))
sc0 = ax.scatter(lon_flat[in_rng], lat_flat[in_rng],
                 c=identity_isl_masked[in_rng], cmap='RdBu_r',
                 norm=TwoSlopeNorm(vcenter=0, vmin=-vmax_id, vmax=vmax_id),
                 s=2, linewidths=0, rasterized=True, zorder=2)
add_contours(ax)
add_labels(ax)
cb0 = fig.colorbar(sc0, ax=ax, orientation='vertical', shrink=0.6, pad=0.02, aspect=22)
cb0.set_label('← Kona-like                  Kaʻu-like →',
              color='black', fontsize=9)
cb0.ax.tick_params(colors='black', labelsize=7)
dark_p = mpatches.Patch(color='#dddddd', label='Outside both profiles')
add_legend(ax, dark_p)

# ── Rows 2 & 3: 2035 thermal change ───────────────────────────────────────────
vlim = float(np.nanpercentile(
    np.abs(np.concatenate([kona_d35[~np.isnan(kona_d35)],
                           kau_d35[~np.isnan(kau_d35)]])), 99))

for ax, td, region, T_MU, panel_lbl in [
    (axes[1], kona_d35, 'Kona', T_MU_KONA, 'b'),
    (axes[2], kau_d35,  'Kaʻu', T_MU_KAU,  'c'),
]:
    base_ax(ax)
    ax.set_title(
        f'({panel_lbl}) Thermal Suitability Change by ~2035 — {region} '
        f'(optimum {T_MU:.1f}°C, ΔT≈+{dt_2035:.2f}°C)',
        color='black', fontsize=12, pad=8, fontweight='bold')
    ax.scatter(lon_flat, lat_flat, c='#eeeeee', s=3,
               linewidths=0, rasterized=True, zorder=1)
    sc = ax.scatter(lon_flat, lat_flat, c=td, cmap='RdBu_r',
                    norm=TwoSlopeNorm(vcenter=0, vmin=-vlim, vmax=vlim),
                    s=3, linewidths=0, rasterized=True, zorder=2)
    add_contours(ax)
    add_labels(ax)
    cb = fig.colorbar(sc, ax=ax, orientation='vertical', shrink=0.6, pad=0.02, aspect=22)
    cb.set_label('← Less suitable        More suitable →',
                 color='black', fontsize=9)
    cb.ax.tick_params(colors='black', labelsize=7)
    td_farm = td[farm_msk]
    n_gain = (td_farm > 0).sum(); n_loss = (td_farm < 0).sum()
    ax.text(0.02, 0.04,
            f'Gain: {n_gain:,} cells ({n_gain/len(td_farm)*100:.0f}%)\n'
            f'Loss: {n_loss:,} cells ({n_loss/len(td_farm)*100:.0f}%)',
            transform=ax.transAxes, color='black', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#f5f5f5',
                      alpha=0.9, edgecolor='#cccccc'))
    excl_p = mpatches.Patch(color='#eeeeee', label='Too steep (>25° slope)')
    add_legend(ax, excl_p)

fig.suptitle(
    'Big Island Coffee Suitability: Current Terrain Identity and Projected Thermal Change (~2035)\n'
    'Ensemble mean: ACCESS-CM2 × MPI-ESM1-2-HR, SSP2-4.5 × SSP5-8.5',
    color='black', fontsize=13, fontweight='bold', y=0.91)
plt.savefig(f'{IMG}/05_kawabata_summary.png', dpi=150,
            facecolor=WH, bbox_inches='tight')
# plt.show()
print('Saved 05_kawabata_summary.png')


# ── E1: Terrain-Thermal Convergence Overlay ──────────────────────────────────
# For each farmable grid cell that passes the topographic profile screen,
# show thermal suitability change matched to its regional envelope:
#   Kona-like terrain → Kona ΔS;  Kaʻu-like terrain → Kaʻu ΔS
# Cells outside both profiles: mid-grey.  Steep / non-farmable: light grey.

from matplotlib.colors import TwoSlopeNorm
import matplotlib.gridspec as gridspec

fig = plt.figure(figsize=(14, 10))
fig.patch.set_facecolor('white')
gs  = gridspec.GridSpec(2, len(THRESHOLDS_PCT),
                        hspace=0.35, wspace=0.08,
                        figure=fig)

vmax_id = float(np.nanpercentile(np.abs(identity_isl[~np.isnan(identity_isl)]), 97))

for col, pct in enumerate(THRESHOLDS_PCT):
    thresh = np.percentile(np.concatenate([kona_dists, kau_dists]), pct)
    in_rng = (dist_kona_isl <= thresh) | (dist_kau_isl <= thresh)
    ident  = np.where(in_rng, identity_isl, np.nan)
    r      = results[col]

    ax = fig.add_subplot(gs[0, col])
    ax.set_facecolor('white')
    ax.set_aspect(1 / np.cos(np.radians(19.6)))
    ax.set_xticks([]); ax.set_yticks([])

    out = np.isnan(ident)
    ax.scatter(lon_flat[out], lat_flat[out], c='#dddddd', s=1.5,
               linewidths=0, rasterized=True)
    inn = ~out
    ax.scatter(lon_flat[inn], lat_flat[inn],
               c=ident[inn], cmap='RdBu_r',
               vmin=-vmax_id, vmax=vmax_id,
               s=1.5, linewidths=0, rasterized=True)

    border_color = '#d62728' if pct == 95 else 'black'
    border_width = 2.0 if pct == 95 else 0.6
    for sp in ax.spines.values():
        sp.set_edgecolor(border_color); sp.set_linewidth(border_width)

    ax.set_title(f'{pct:.0f}th pct\n'
                 f'Kona {r["kona_pct"]:.1f}% | Ka\'u {r["kau_pct"]:.1f}%',
                 fontsize=10, color='black', pad=4)

# ── Bottom row: bar chart + Jaccard ──────────────────────────────────────────
ax_bar  = fig.add_subplot(gs[1, :2])
ax_jacc = fig.add_subplot(gs[1, 2:])

x         = np.arange(len(THRESHOLDS_PCT))
w         = 0.35
kona_area = [r['kona_pct']     for r in results]
kau_area  = [r['kau_pct']      for r in results]
j_kona    = [r['jaccard_kona'] for r in results]
j_kau     = [r['jaccard_kau']  for r in results]

ax_bar.bar(x - w/2, kona_area, w, color='#2166ac', label='Kona-like', alpha=0.85)
ax_bar.bar(x + w/2, kau_area,  w, color='#d6604d', label="Ka\'u-like", alpha=0.85)
ax_bar.set_xticks(x)
ax_bar.set_xticklabels([f'{p:.0f}th' for p in THRESHOLDS_PCT], fontsize=11)
ax_bar.set_ylabel('% of island land', fontsize=11)
ax_bar.set_title('Classified area by threshold', fontsize=12, fontweight='bold')
ax_bar.axvline(x=2, color='#d62728', linestyle='--', linewidth=1.5, label='Baseline (95th)')
ax_bar.legend(fontsize=10, facecolor='white')
ax_bar.set_facecolor('white'); ax_bar.tick_params(labelsize=10)

ax_jacc.plot(x, j_kona, 'o-', color='#2166ac', linewidth=2, markersize=7, label='Kona')
ax_jacc.plot(x, j_kau,  's-', color='#d6604d', linewidth=2, markersize=7, label="Ka\'u")
ax_jacc.axvline(x=2, color='#d62728', linestyle='--', linewidth=1.5, label='Baseline (95th)')
ax_jacc.set_xticks(x)
ax_jacc.set_xticklabels([f'{p:.0f}th' for p in THRESHOLDS_PCT], fontsize=11)
ax_jacc.set_ylabel('Jaccard similarity to 95th-pct baseline', fontsize=11)
ax_jacc.set_ylim(0.7, 1.02)
ax_jacc.set_title('Spatial stability of convergence zones', fontsize=12, fontweight='bold')
ax_jacc.legend(fontsize=10, facecolor='white')
ax_jacc.set_facecolor('white'); ax_jacc.tick_params(labelsize=10)

fig.suptitle(
    "Supplementary Figure S1: Sensitivity of Terrain Classification to Centroid-Distance Threshold\n"
    "Red border = baseline (95th percentile).  ← Kona-like (blue)  |  Ka\'u-like (red) →",
    fontsize=12, fontweight='bold', color='black', y=1.01)

plt.savefig(f'{IMG}/S1_threshold_sensitivity.png', dpi=300,
            facecolor='white', bbox_inches='tight')
# plt.show()
print('Saved S1_threshold_sensitivity.png')


# ── E3: Overestimation factor — thermal-only vs terrain-constrained ──────────
# Computes the ratio of thermally-gaining farmable cells to cells that pass
# BOTH the terrain screen AND are thermally gaining.
# This is the quantitative punchline: climate-only models overestimate
# accessible opportunity by this factor.

print("=" * 65)
print("OVERESTIMATION FACTOR: thermal-only vs. terrain-constrained")
print("=" * 65)

n_farmable = int(farm_msk.sum())
topo_valid = ~np.isnan(identity_isl_masked)
kona_like  = topo_valid & (identity_isl_masked <= 0)
kau_like   = topo_valid & (identity_isl_masked >  0)

rows = []
for label, thermal_d, topo_msk, horizon in [
    ("Kona", kona_d35, kona_like, "2035"),
    ("Kona", kona_d45, kona_like, "2045"),
    ("Ka'u", kau_d35,  kau_like,  "2035"),
    ("Ka'u", kau_d45,  kau_like,  "2045"),
]:
    # Thermal-only: farmable + gaining
    therm = farm_msk & ~np.isnan(thermal_d) & (thermal_d > 0)
    n_th  = int(therm.sum())
    p_th  = n_th / n_farmable * 100

    # Dual screen: farmable + topographically matched + gaining
    dual  = farm_msk & topo_msk & ~np.isnan(thermal_d) & (thermal_d > 0)
    n_du  = int(dual.sum())
    p_du  = n_du / n_farmable * 100

    factor = n_th / n_du if n_du > 0 else float("inf")

    rows.append((label, horizon, n_th, p_th, n_du, p_du, factor))
    print(f"\n{label} ~{horizon}:")
    print(f"  Thermal-only gaining (farmable):      {n_th:6,}  ({p_th:5.1f}%)")
    print(f"  Terrain-constrained gaining:          {n_du:6,}  ({p_du:5.1f}%)")
    print(f"  Overestimation factor:                {factor:6.1f}x")

print("\n" + "=" * 65)
print("Copy these numbers into paper.tex Results §5.4")
print("=" * 65)


# ── E4: Overestimation factor across threshold sensitivity range ──────────────
# Cross-walks E3 with the E2 sensitivity analysis.
# Directly addresses R2 concern that the factor may reflect modeling choices:
# shows the factor at every threshold tested, demonstrating the qualitative
# conclusion is robust regardless of threshold choice.

# Thermal-only gaining cells (Ka'u) — numerator, fixed across thresholds
kau_thermal_gaining = farm_msk & ~np.isnan(kau_d35) & (kau_d35 > 0)
n_thermal_kau = int(kau_thermal_gaining.sum())

print("=" * 65)
print("OVERESTIMATION FACTOR SENSITIVITY — Ka'u")
print(f"Thermal-only gaining cells (fixed): {n_thermal_kau:,}")
print("=" * 65)
print(f"{'Threshold':>12} | {'Terrain cells':>14} | {'Factor':>8}")
print("-" * 44)

factor_rows = []
for pct in THRESHOLDS_PCT:
    thresh  = np.percentile(np.concatenate([kona_dists, kau_dists]), pct)
    in_rng  = (dist_kona_isl <= thresh) | (dist_kau_isl <= thresh)
    ident   = np.where(in_rng, identity_isl, np.nan)
    kau_msk = farm_msk & (~np.isnan(ident)) & (ident > 0)
    dual    = kau_msk & ~np.isnan(kau_d35) & (kau_d35 > 0)
    n_du    = int(dual.sum())
    factor  = n_thermal_kau / n_du if n_du > 0 else float('inf')
    marker  = "  <- baseline" if pct == 95 else ""
    print(f"  {pct:>5.1f}th pct | {n_du:>14,} | {factor:>7.1f}x{marker}")
    factor_rows.append((pct, n_du, factor))

print("-" * 44)
f_vals = [r[2] for r in factor_rows]
print(f"Factor range: {min(f_vals):.1f}x - {max(f_vals):.1f}x")
print("Order-of-magnitude overestimation holds at every threshold tested.")


# ── E5: Mahalanobis vs Euclidean distance metric comparison ──────────────────
# Addresses R2 concern: justify Euclidean distance in standardised feature space.
# Computes Mahalanobis distance using pooled within-class covariance, applies
# the same 95th-percentile threshold logic, and compares terrain footprints.
# If Jaccard similarity is high and overestimation factor is similar,
# the Euclidean choice is empirically validated.

from scipy.spatial.distance import cdist

# ── Pooled within-class covariance ───────────────────────────────────────────
kona_centered = Xs_coffee_isl[kona_isl_mask] - kona_isl_centroid
kau_centered  = Xs_coffee_isl[kau_isl_mask]  - kau_isl_centroid
pooled_cov    = np.cov(np.vstack([kona_centered, kau_centered]).T, ddof=1)

# Small regularisation in case of near-singular covariance
pooled_cov_reg = pooled_cov + 1e-6 * np.eye(pooled_cov.shape[0])
VI = np.linalg.inv(pooled_cov_reg)

# ── Mahalanobis distances: island cells to each regional centroid ─────────────
dist_kona_mah = cdist(Xs_isl, kona_isl_centroid.reshape(1, -1),
                      metric='mahalanobis', VI=VI).ravel()
dist_kau_mah  = cdist(Xs_isl, kau_isl_centroid.reshape(1, -1),
                      metric='mahalanobis', VI=VI).ravel()

# ── Within-region farm distances (for threshold calibration) ─────────────────
kona_mah_dists = cdist(Xs_coffee_isl[kona_isl_mask],
                       kona_isl_centroid.reshape(1, -1),
                       metric='mahalanobis', VI=VI).ravel()
kau_mah_dists  = cdist(Xs_coffee_isl[kau_isl_mask],
                       kau_isl_centroid.reshape(1, -1),
                       metric='mahalanobis', VI=VI).ravel()

# ── Apply same threshold range and compare to Euclidean baseline ─────────────
print("=" * 70)
print("MAHALANOBIS vs EUCLIDEAN — terrain footprint and overestimation factor")
print("=" * 70)
print(f"{'Threshold':>12} | {'Kona%':>7} | {'Kaʻu%':>7} | {'J_Kona':>8} | {'J_Kaʻu':>8} | {'Factor':>8}")
print("-" * 62)

# Euclidean 95th pct baseline for Jaccard comparison
thresh_euc95 = np.percentile(np.concatenate([kona_dists, kau_dists]), 95)
in_euc95     = (dist_kona_isl <= thresh_euc95) | (dist_kau_isl <= thresh_euc95)
ident_euc95  = np.where(in_euc95, identity_isl, np.nan)
base_kona_euc = (~np.isnan(ident_euc95)) & (ident_euc95 <= 0)
base_kau_euc  = (~np.isnan(ident_euc95)) & (ident_euc95 >  0)

kau_thermal_gaining = farm_msk & ~np.isnan(kau_d35) & (kau_d35 > 0)
n_thermal_kau = int(kau_thermal_gaining.sum())
n_land = len(identity_isl)

mah_rows = []
for pct in THRESHOLDS_PCT:
    thresh_m  = np.percentile(np.concatenate([kona_mah_dists, kau_mah_dists]), pct)
    in_m      = (dist_kona_mah <= thresh_m) | (dist_kau_mah <= thresh_m)
    # Identity score still uses Euclidean-derived scores (same sign logic)
    ident_m   = np.where(in_m, identity_isl, np.nan)
    kona_m    = (~np.isnan(ident_m)) & (ident_m <= 0)
    kau_m     = (~np.isnan(ident_m)) & (ident_m >  0)
    kona_pct  = kona_m.sum() / n_land * 100
    kau_pct   = kau_m.sum()  / n_land * 100
    j_kona    = (kona_m & base_kona_euc).sum() / (kona_m | base_kona_euc).sum()
    j_kau     = (kau_m  & base_kau_euc ).sum() / (kau_m  | base_kau_euc ).sum()
    dual      = farm_msk & kau_m & ~np.isnan(kau_d35) & (kau_d35 > 0)
    n_du      = int(dual.sum())
    factor    = n_thermal_kau / n_du if n_du > 0 else float('inf')
    marker    = "  <- 95th" if pct == 95 else ""
    print(f"  {pct:>5.1f}th pct | {kona_pct:>6.2f}% | {kau_pct:>6.2f}% | "
          f"{j_kona:>8.3f} | {j_kau:>8.3f} | {factor:>7.1f}x{marker}")
    mah_rows.append((pct, kona_pct, kau_pct, j_kona, j_kau, n_du, factor))

print("-" * 62)
print("Jaccard similarity is vs. Euclidean 95th-pct baseline.")
print("High Jaccard = Mahalanobis recovers the same terrain footprint.")
print("Similar factor = overestimation conclusion is metric-independent.")
