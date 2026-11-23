"""Plotting helpers so every figure in the series looks the same.

Usage inside a post (code cells run with the post's folder as the working directory):

    import os, sys
    sys.path.insert(0, os.environ.get("QUARTO_PROJECT_DIR", "../.."))
    from _lib.plots import load, heatmap, line, bars

    res = load("05-e1-grid-fp32.json")            # reads <project>/data/05-e1-grid-fp32.json
    heatmap(values, x=strengths, y=layers, center=0, data=res)

Conventions
- Data lives in `data/*.json` (copied from the lab repo's `results/`). Posts never hard-code numbers they plot.
- A JSON file with `"_placeholder": true` gets a loud PLACEHOLDER watermark, so fake data is never mistaken for results.
- Pass `source="..."` to print a source line under the figure (required for numbers quoted from other work).
- `save(fig, "05-layer-strength")` also writes `figures/<name>.svg` for reuse outside the blog (slides, README).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import matplotlib

if "ipykernel" not in sys.modules:   # inside Quarto/Jupyter keep the inline backend, or figures never show
    matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm  # noqa: E402

# ---------------------------------------------------------------- palette
# One categorical palette for the whole series (colour-blind friendly, readable on light and dark pages).
PALETTE = {
    "blue": "#2b6cb0",    # main series / "steered"
    "orange": "#dd6b20",  # second series
    "teal": "#2c9a8a",
    "purple": "#7b5cc4",
    "red": "#c53030",     # broken outputs ("tomato tomato tomato")
    "grey": "#8a8f98",    # controls (random direction, no push)
}
CYCLE = [PALETTE[k] for k in ("blue", "orange", "teal", "purple", "red", "grey")]

# Colours bound to a meaning: use these names in every post so a colour means the same thing everywhere.
ROLE = {
    "steered": PALETTE["blue"],
    "baseline": PALETTE["grey"],
    "control": PALETTE["grey"],
    "removal": PALETTE["teal"],
    "broken": PALETTE["red"],
    "tune": PALETTE["orange"],
    "test": PALETTE["blue"],
}

# Diverging map for signed scores (mood = P(joy) - P(sadness)): blue = sadder, orange = happier.
DIVERGING = LinearSegmentedColormap.from_list("steer_div", ["#2b6cb0", "#f4f1ea", "#dd6b20"])
# Sequential map for 0..1 rates (success rate, gibberish rate).
SEQUENTIAL = LinearSegmentedColormap.from_list("steer_seq", ["#f4f1ea", "#7fb3f0", "#2b6cb0", "#1a365d"])

MUTED = "#6b7178"  # axis text: readable on both the light and the dark page background


def _style():
    plt.rcParams.update({
        "figure.figsize": (6.4, 3.6),
        "figure.dpi": 150,
        "savefig.bbox": "tight",
        "savefig.transparent": True,   # figure sits on either theme's background
        "font.family": "sans-serif",
        "font.sans-serif": ["Source Sans 3", "DejaVu Sans", "Arial"],
        "font.size": 10,
        "text.color": MUTED,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.titlecolor": MUTED,
        "axes.labelcolor": MUTED,
        "axes.edgecolor": "#8a8f98",
        "axes.facecolor": "none",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": "#8a8f98",
        "grid.alpha": 0.25,
        "grid.linewidth": 0.6,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "legend.frameon": False,
        "legend.labelcolor": MUTED,
        "axes.prop_cycle": matplotlib.cycler(color=CYCLE),
        "lines.linewidth": 2.0,
        "lines.markersize": 5,
    })


_style()

# ---------------------------------------------------------------- data


def project_dir() -> Path:
    """The blog root: $QUARTO_PROJECT_DIR during a render, otherwise the nearest parent with _quarto.yml."""
    env = os.environ.get("QUARTO_PROJECT_DIR")
    if env:
        return Path(env)
    here = Path.cwd().resolve()
    for p in (here, *here.parents):
        if (p / "_quarto.yml").exists():
            return p
    return Path(__file__).resolve().parents[1]


def load(name: str) -> dict:
    """Read data/<name>. Raises a clear error if the result hasn't been copied over yet."""
    path = project_dir() / "data" / name
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Copy it from the lab repo's results/ (see README).")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def is_placeholder(data: dict | None) -> bool:
    return bool(data and data.get("_placeholder"))


def _mark(ax, data):
    if is_placeholder(data):
        ax.text(0.5, 0.5, "PLACEHOLDER", transform=ax.transAxes, ha="center", va="center",
                fontsize=28, fontweight="bold", color=PALETTE["red"], alpha=0.25, rotation=18, zorder=10)


def _source(fig, source):
    if source:
        fig.text(0.01, -0.02, f"Source: {source}", fontsize=7.5, color="#8a8f98", ha="left", va="top")


def save(fig, name: str, fmt: str = "svg") -> Path:
    """Also write figures/<name>.<fmt>, for reuse outside the blog."""
    out = project_dir() / "figures" / f"{name}.{fmt}"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    return out


def _labels(ax, title, xlabel, ylabel):
    if title:
        ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)


# ---------------------------------------------------------------- plots


def heatmap(values, x, y, *, title=None, xlabel=None, ylabel=None, cbar_label=None, center=None,
            cmap=None, annotate=True, fmt="{:.2f}", data=None, source=None, ax=None):
    """Grid of values[i][j] at row y[i], column x[j] (row 0 at the bottom).

    `center=0` gives a diverging map centred on 0 (for signed scores like mood); otherwise a sequential map.
    """
    v = np.asarray(values, dtype=float)
    if ax is None:
        fig, ax = plt.subplots(figsize=(1.6 + 0.62 * len(x), 1.0 + 0.38 * len(y)))
    else:
        fig = ax.figure
    if center is not None:
        span = float(np.nanmax(np.abs(v - center))) or 1.0
        norm = TwoSlopeNorm(vcenter=center, vmin=center - span, vmax=center + span)
        im = ax.imshow(v, cmap=cmap or DIVERGING, norm=norm, aspect="auto", origin="lower")
    else:
        im = ax.imshow(v, cmap=cmap or SEQUENTIAL, aspect="auto", origin="lower")
    ax.set_xticks(range(len(x)), [str(t) for t in x])
    ax.set_yticks(range(len(y)), [str(t) for t in y])
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    if annotate and v.size <= 400:
        for i in range(v.shape[0]):
            for j in range(v.shape[1]):
                if np.isfinite(v[i, j]):
                    r, g, b, _ = im.cmap(im.norm(v[i, j]))
                    dark = 0.299 * r + 0.587 * g + 0.114 * b < 0.5
                    ax.text(j, i, fmt.format(v[i, j]), ha="center", va="center", fontsize=7,
                            color="white" if dark else "#1f2328")
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cb.outline.set_visible(False)
    if cbar_label:
        cb.set_label(cbar_label)
    _labels(ax, title, xlabel, ylabel)
    _mark(ax, data)
    _source(fig, source)
    return fig, ax


def line(x, series: dict, *, title=None, xlabel=None, ylabel=None, hlines: dict | None = None,
         colors: dict | None = None, markers=True, data=None, source=None, ax=None, **kw):
    """One line per entry of `series` ({label: ys}). `hlines` ({label: y}) adds dashed reference lines (controls)."""
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure
    colors = colors or {}
    for i, (label, ys) in enumerate(series.items()):
        ax.plot(x, ys, marker="o" if markers else None, color=colors.get(label, CYCLE[i % len(CYCLE)]),
                label=label, **kw)
    for label, yv in (hlines or {}).items():
        ax.axhline(yv, ls="--", lw=1.2, color=colors.get(label, ROLE["control"]), label=label)
    _labels(ax, title, xlabel, ylabel)
    if len(series) + len(hlines or {}) > 1:
        ax.legend(loc="best")
    _mark(ax, data)
    _source(fig, source)
    return fig, ax


def bars(labels, values, *, title=None, ylabel=None, colors=None, fmt="{:.3g}", errors=None,
         data=None, source=None, ax=None, horizontal=False):
    """Bar chart with value labels. Good for the A/B/C/D speed table and tune-vs-test comparisons."""
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure
    colors = colors or [CYCLE[i % len(CYCLE)] for i in range(len(labels))]
    if horizontal:
        rects = ax.barh(labels, values, color=colors, xerr=errors)
        ax.grid(axis="y", visible=False)
        ax.invert_yaxis()
        if ylabel:
            ax.set_xlabel(ylabel)
    else:
        rects = ax.bar(labels, values, color=colors, yerr=errors)
        ax.grid(axis="x", visible=False)
        if ylabel:
            ax.set_ylabel(ylabel)
    ax.bar_label(rects, labels=[fmt.format(v) for v in values], padding=3, fontsize=8, color=MUTED)
    if title:
        ax.set_title(title)
    _mark(ax, data)
    _source(fig, source)
    return fig, ax
