"""Three AGU-poster GIFs, all driven by the same dt sweep over pipeline.py's
model. No new statistics -- reuses load_island/load_farms/envelope/screen/
pooled_union exactly as notebooks 03/04 do.

  1. temperature.gif      -- T + dt across the island (uniform warming)
  2. envelope_upslope.gif -- C(dt): the thermal band migrating upslope
  3. envelope_screened.gif-- F(dt) = C(dt) & S: same band, screen applied

Run: python make_gifs.py
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.animation import FuncAnimation, PillowWriter
import pipeline as P

OUT = 'figures'
os.makedirs(OUT, exist_ok=True)
FARM_GRAY, LOST_RED, KEEP_GREEN = '#cfcfcf', '#c1440e', '#7fb069'
NOT_FARM = '#f2f2f2'

DTS = np.linspace(0.0, P.DT_HORIZON['2045'], 25)  # 0 -> 2045, then hard-cut restart


def to_grid(isl, values, fill=np.nan):
    g = np.full(isl['land'].shape, fill)
    g.ravel()[np.where(isl['land'].ravel())[0]] = values
    return g


def crop_box(isl):
    rr, cc = np.where(isl['land'])
    H, W = isl['land'].shape
    return (max(0, rr.min() - 3), rr.max() + 4, max(0, cc.min() - 3), cc.max() + 4)


def animate(fig, ax, draw_frame, name, fps=8):
    anim = FuncAnimation(fig, draw_frame, frames=len(DTS), blit=False)
    path = f'{OUT}/{name}'
    anim.save(path, writer=PillowWriter(fps=fps))
    plt.close(fig)
    print(path)


def gif_temperature(isl):
    r0, r1, c0, c1 = crop_box(isl)
    vmin, vmax = np.nanmin(isl['T']), np.nanmax(isl['T']) + DTS.max()
    fig, ax = plt.subplots(figsize=(5, 5.5))
    im = ax.imshow(to_grid(isl, isl['T'])[r0:r1, c0:c1], cmap='inferno',
                    vmin=vmin, vmax=vmax, interpolation='nearest')
    ax.set_xticks([]); ax.set_yticks([])
    title = ax.set_title('T + ΔT, ΔT = +0.00 °C')
    fig.colorbar(im, ax=ax, label='temperature (°C)', shrink=0.8)
    fig.tight_layout()

    def frame(i):
        dt = DTS[i]
        im.set_data(to_grid(isl, isl['T'] + dt)[r0:r1, c0:c1])
        title.set_text(f'T + ΔT, ΔT = +{dt:.2f} °C')
        return im, title

    animate(fig, ax, frame, 'temperature.gif')


def gif_envelope_upslope(isl, FT, FTemp, reg):
    idx = np.arange(len(FT))
    envs = {r: P.envelope(FTemp, reg, idx, r) for r in ('kona', 'kau')}
    r0, r1, c0, c1 = crop_box(isl)
    cm = ListedColormap([FARM_GRAY, KEEP_GREEN])
    fig, ax = plt.subplots(figsize=(5, 5.5))
    im = ax.imshow(np.zeros(isl['land'].shape)[r0:r1, c0:c1], cmap=cm,
                    norm=BoundaryNorm([0, 1, 2], 2), interpolation='nearest')
    ax.set_xticks([]); ax.set_yticks([])
    title = ax.set_title('Thermal band C(ΔT), ΔT = +0.00 °C')
    import matplotlib.patches as mp
    ax.legend(handles=[mp.Patch(color=KEEP_GREEN, label='thermal band C(ΔT)')],
              frameon=False, fontsize=8, loc='upper left', bbox_to_anchor=(0.0, -0.02))
    fig.tight_layout()

    def frame(i):
        # districts have effectively the same niche (notebook 03) -- pooled,
        # same convention pooled_union() uses for the screened GIF
        dt = DTS[i]
        code = np.full(len(isl['X']), 0.5)
        inband = np.zeros(len(isl['X']), bool)
        for r in ('kona', 'kau'):
            mu, sg = envs[r]
            inband |= np.exp(-0.5 * ((isl['T'] + dt - mu) / sg) ** 2) > 0.5
        code[isl['farmable'] & inband] = 1.5
        im.set_data(to_grid(isl, code)[r0:r1, c0:c1])
        title.set_text(f'Thermal band C(ΔT), ΔT = +{dt:.2f} °C')
        return im, title

    animate(fig, ax, frame, 'envelope_upslope.gif')


def gif_envelope_screened(isl, FT, FTemp, reg):
    r0, r1, c0, c1 = crop_box(isl)
    _, u0 = P.pooled_union(isl, FT, FTemp, reg, dt=0.0)
    cm = ListedColormap([NOT_FARM, FARM_GRAY, KEEP_GREEN, LOST_RED])
    fig, ax = plt.subplots(figsize=(5, 5.5))
    im = ax.imshow(np.zeros(isl['land'].shape)[r0:r1, c0:c1], cmap=cm,
                    norm=BoundaryNorm([0, 1, 2, 3, 4], 4), interpolation='nearest')
    ax.set_xticks([]); ax.set_yticks([])
    title = ax.set_title('F(ΔT) = C(ΔT) ∩ S, ΔT = +0.00 °C')
    import matplotlib.patches as mp
    ax.legend(handles=[mp.Patch(color=KEEP_GREEN, label='feasible now'),
                        mp.Patch(color=LOST_RED, label='lost since +0 °C'),
                        mp.Patch(color=FARM_GRAY, label='farmable, not feasible'),
                        mp.Patch(color=NOT_FARM, label='not farmable (slope/lava)')],
              frameon=False, fontsize=8, loc='upper left', bbox_to_anchor=(0.0, -0.02))
    fig.tight_layout()

    def frame(i):
        dt = DTS[i]
        _, u = P.pooled_union(isl, FT, FTemp, reg, dt=dt)
        code = np.full(len(isl['X']), 0.5)       # not farmable
        code[isl['farmable']] = 1.5               # farmable, not (yet) feasible
        code[u] = 2.5                             # feasible now
        code[u0 & ~u] = 3.5                       # feasible at ΔT=0, lost since
        im.set_data(to_grid(isl, code)[r0:r1, c0:c1])
        title.set_text(f'F(ΔT) = C(ΔT) ∩ S, ΔT = +{dt:.2f} °C')
        return im, title

    animate(fig, ax, frame, 'envelope_screened.gif')


if __name__ == '__main__':
    isl = P.load_island()
    FT, FTemp, reg, xy = P.load_farms(isl)
    gif_temperature(isl)
    gif_envelope_upslope(isl, FT, FTemp, reg)
    gif_envelope_screened(isl, FT, FTemp, reg)
