"""
Dark-theme grafik üretici — deep navy + neon accent palette.
Tüm değerler ham TL cinsinden plot edilir; _fmt_k formatter axis etiketlerini
"500K" / "1.2M" formatında gösterir.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from pathlib import Path

# ─── Renk paleti ─────────────────────────────────────────────────────────
BG       = "#0a0e1a"
SURFACE  = "#111827"
SURFACE2 = "#1a2234"
BORDER   = "#1e2d45"
TEXT     = "#f1f5f9"
TEXT2    = "#64748b"
GRIDCOL  = "#1a2540"

FIRM_COLORS = {
    "Firma_A": "#6366f1",
    "Firma_B": "#06b6d4",
    "Firma_C": "#10b981",
    "Firma_D": "#ef4444",
    "Firma_E": "#f59e0b",
    "Firma_F": "#8b5cf6",
}

ACCENT  = "#6366f1"
CYAN    = "#06b6d4"
EMERALD = "#10b981"
AMBER   = "#f59e0b"
RED     = "#ef4444"
PURPLE  = "#8b5cf6"

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)


# ─── Yardımcılar ─────────────────────────────────────────────────────────
def _fmt_k(x, _):
    """Ham TL değerini okunabilir eksen etiketi: 1_500_000 → '1.5M'."""
    ax = abs(x)
    if ax >= 1_000_000:
        return f"{x/1_000_000:.1f}M"
    if ax >= 1_000:
        return f"{x/1_000:.0f}K"
    return f"{x:.0f}"


def _dark(fig, axes):
    fig.patch.set_facecolor(BG)
    for ax in axes:
        ax.set_facecolor(SURFACE)
        ax.tick_params(colors=TEXT2, labelsize=9)
        ax.xaxis.label.set_color(TEXT2)
        ax.yaxis.label.set_color(TEXT2)
        ax.title.set_color(TEXT)
        for sp in ax.spines.values():
            sp.set_edgecolor(BORDER)
        ax.grid(color=GRIDCOL, linewidth=0.5, linestyle="--", alpha=1)
        ax.set_axisbelow(True)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(_fmt_k))


def _glow(ax, x, h, w=0.6, color=ACCENT, bottom=0):
    ax.bar(x, h, width=w,        bottom=bottom, color=color, alpha=0.92, zorder=3)
    ax.bar(x, h, width=w + 0.16, bottom=bottom, color=color, alpha=0.07, zorder=2)


def _save(fig, name):
    p = OUTPUT / f"{name}.png"
    fig.savefig(p, dpi=160, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    return str(p)


def _bar_label(ax, xi, val_raw, color, pad_pct=0.02, suffix=""):
    """Bar üstüne akıllı etiket."""
    top = ax.get_ylim()[1]
    label = _fmt_k(val_raw, None) + suffix
    ax.text(xi, val_raw + top * pad_pct, label,
            ha="center", va="bottom", fontsize=8.5,
            color=color, fontweight="bold")


# ─── 1. Aylık Net Satış Trendi ────────────────────────────────────────────
def plot_monthly_sales(actual_df: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(13, 5))
    _dark(fig, [ax])

    for firma, grp in actual_df.groupby("firma"):
        grp   = grp.sort_values("ay")
        color = FIRM_COLORS.get(firma, ACCENT)
        ax.plot(grp["ay"], grp["net_satis"],
                marker="o", color=color, linewidth=2.2,
                markersize=7, markerfacecolor=BG, markeredgewidth=2,
                label=firma, zorder=4)

    ax.set_title("Aylık Net Satış  ·  Ay 1–5 Gerçekleşen",
                 fontsize=14, fontweight="bold", color=TEXT, pad=14)
    ax.set_xlabel("Ay", fontsize=10)
    ax.set_ylabel("Net Satış (₺)", fontsize=10)
    ax.set_xticks(range(1, 6))
    ax.legend(framealpha=0, labelcolor=TEXT, fontsize=9, ncol=2,
              loc="upper left")
    fig.tight_layout()
    return _save(fig, "01_aylik_net_satis")


# ─── 2. Katkı Marjı ───────────────────────────────────────────────────────
def plot_contribution_margin(summary_df: pd.DataFrame) -> str:
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    _dark(fig, axes)

    firms  = list(summary_df["firma"])
    colors = [FIRM_COLORS.get(f, ACCENT) for f in firms]
    x      = np.arange(len(firms))

    # Sol: katkı kârı (ham TL)
    ax = axes[0]
    vals = list(summary_df["katki_kari_toplam"])
    for xi, (val, color) in enumerate(zip(vals, colors)):
        _glow(ax, xi, val, color=color)
    ax.set_xticks(x); ax.set_xticklabels(firms, rotation=28, ha="right")
    ax.set_title("Katkı Kârı", fontsize=12, fontweight="bold", color=TEXT)
    ax.set_ylabel("₺", fontsize=10)
    # Etiketler: sonradan ylim belli olunca
    fig.canvas.draw()
    for xi, (val, color) in enumerate(zip(vals, colors)):
        _bar_label(ax, xi, val, color)

    # Sağ: katkı marjı %
    ax = axes[1]
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    pcts = list(summary_df["katki_marji"] * 100)
    for xi, (pct, color) in enumerate(zip(pcts, colors)):
        ax.bar(xi, pct, width=0.6, color=color, alpha=0.92, zorder=3)
        ax.bar(xi, pct, width=0.76, color=color, alpha=0.07, zorder=2)
        ax.text(xi, pct + 0.4, f"{pct:.1f}%", ha="center", va="bottom",
                fontsize=8.5, color=color, fontweight="bold")
    ax.axhline(y=15, color=AMBER, linestyle="--", linewidth=1.4,
               label="Hedef %15", zorder=5)
    ax.set_xticks(x); ax.set_xticklabels(firms, rotation=28, ha="right")
    ax.set_title("Katkı Marjı", fontsize=12, fontweight="bold", color=TEXT)
    ax.set_ylabel("%", fontsize=10)
    ax.legend(framealpha=0, labelcolor=TEXT, fontsize=9)

    fig.suptitle("Firma Bazlı Katkı Kârı Analizi  ·  Ay 1–5",
                 fontsize=14, fontweight="bold", color=TEXT, y=1.02)
    fig.tight_layout()
    return _save(fig, "02_katki_marji")


# ─── 3. Efektif Ödeme Oranı ───────────────────────────────────────────────
def plot_effective_payment(summary_df: pd.DataFrame) -> str:
    from config.settings import MAX_REWARD_RATE, CONTRACT_COMMISSION_RATE
    threshold = (MAX_REWARD_RATE + CONTRACT_COMMISSION_RATE) * 100

    fig, ax = plt.subplots(figsize=(11, 5))
    _dark(fig, [ax])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))

    firms = list(summary_df["firma"])
    x     = np.arange(len(firms))
    vals  = list(summary_df["efektif_odeme_orani"] * 100)

    for xi, (val, firma) in enumerate(zip(vals, firms)):
        color = RED if val > threshold else FIRM_COLORS.get(firma, ACCENT)
        ax.bar(xi, val, width=0.6, color=color, alpha=0.92, zorder=3)
        ax.bar(xi, val, width=0.76, color=color, alpha=0.07, zorder=2)
        ax.text(xi, val + 0.2, f"{val:.1f}%", ha="center", va="bottom",
                fontsize=9, color=color, fontweight="bold")

    ax.axhline(y=threshold, color=AMBER, linestyle="--", linewidth=1.6,
               label=f"Guardrail  {threshold:.0f}%", zorder=5)
    ax.set_xticks(x); ax.set_xticklabels(firms, rotation=28, ha="right")
    ax.set_title("Efektif Ödeme Oranı  ·  (Komisyon + Ödül) / Net Satış",
                 fontsize=13, fontweight="bold", color=TEXT, pad=12)
    ax.set_ylabel("%", fontsize=10)
    ax.legend(framealpha=0, labelcolor=TEXT, fontsize=9)
    fig.tight_layout()
    return _save(fig, "03_efektif_odeme_orani")


# ─── 4. Waterfall ─────────────────────────────────────────────────────────
def plot_waterfall(waterfall_df: pd.DataFrame, firma: str) -> str:
    fig, ax = plt.subplots(figsize=(12, 6))
    _dark(fig, [ax])

    steps  = waterfall_df["adim"].tolist()
    values = waterfall_df["deger"].tolist()
    types  = waterfall_df["tip"].tolist()

    running = 0
    bottoms, heights, bar_colors = [], [], []
    for v, t in zip(values, types):
        if t in ("bar", "total"):
            bottoms.append(0); heights.append(v)
            bar_colors.append(ACCENT if v > 0 else RED)
            running = v
        else:
            if v >= 0:
                bottoms.append(running); heights.append(v); bar_colors.append(EMERALD)
            else:
                bottoms.append(running + v); heights.append(-v); bar_colors.append(RED)
            running += v

    x   = np.arange(len(steps))
    top = max(b + h for b, h in zip(bottoms, heights))
    pad = top * 0.025

    for xi, (h, b, c) in enumerate(zip(heights, bottoms, bar_colors)):
        ax.bar(xi, h, bottom=b, color=c, width=0.55, alpha=0.92, zorder=3)
        ax.bar(xi, h, bottom=b, color=c, width=0.70, alpha=0.07, zorder=2)

    for xi, (v, h, b, c) in enumerate(zip(values, heights, bottoms, bar_colors)):
        sign = "+" if v >= 0 else ""
        label = f"{sign}{_fmt_k(v, None)}"
        ax.text(xi, b + h + pad, label,
                ha="center", va="bottom", fontsize=8,
                color=EMERALD if v >= 0 else RED, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(steps, rotation=30, ha="right", fontsize=9, color=TEXT)
    ax.set_title(f"Waterfall  ·  {firma}  ·  Ay 1–5 Kümülatif",
                 fontsize=12, fontweight="bold", color=TEXT, pad=12)
    ax.set_ylabel("₺", fontsize=10)
    ax.set_xlim(-0.6, len(steps) - 0.4)
    fig.tight_layout()
    return _save(fig, f"04_waterfall_{firma}")


# ─── 5. Yıl Sonu Senaryolar ───────────────────────────────────────────────
def plot_yearend_scenarios(yearend_df: pd.DataFrame) -> str:
    firms = list(yearend_df["firma"].unique())
    scs   = [("Kötümser", RED), ("Baz", ACCENT), ("İyimser", EMERALD)]
    w     = 0.22
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    _dark(fig, axes)

    for ax_i, (metric, ylabel, title) in enumerate([
        ("net_satis_yil",  "₺", "Yıl Sonu Net Satış"),
        ("katki_kari_yil", "₺", "Yıl Sonu Katkı Kârı"),
    ]):
        ax = axes[ax_i]
        x  = np.arange(len(firms))
        for i, (sc_lbl, color) in enumerate(scs):
            scd  = yearend_df[yearend_df["senaryo"] == sc_lbl]
            vals = [scd[scd["firma"] == f][metric].values[0]
                    if len(scd[scd["firma"] == f]) > 0 else 0 for f in firms]
            for xi, val in zip(x + (i - 1) * w, vals):
                _glow(ax, xi, val, w=w - 0.03, color=color)
        ax.set_xticks(x); ax.set_xticklabels(firms, rotation=28, ha="right", fontsize=9, color=TEXT)
        ax.set_title(title, fontsize=12, fontweight="bold", color=TEXT)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.legend(handles=[mpatches.Patch(color=c, label=s) for s, c in scs],
                  framealpha=0, labelcolor=TEXT, fontsize=9)

    fig.suptitle("Yıl Sonu Tahmin Senaryoları  ·  Kümülatif Ay 1–12",
                 fontsize=14, fontweight="bold", color=TEXT, y=1.02)
    fig.tight_layout()
    return _save(fig, "05_yilsonu_senaryolar")


# ─── 6. Q3 Senaryolar ─────────────────────────────────────────────────────
def plot_q3_scenarios(q3_df: pd.DataFrame) -> str:
    firms = list(q3_df["firma"].unique())
    scs   = [("Kötümser", RED), ("Baz", ACCENT), ("İyimser", EMERALD)]
    w     = 0.22
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    _dark(fig, axes)

    for ax_i, (metric, ylabel, title) in enumerate([
        ("net_satis_q3",  "₺", "Q3 Net Satış  (Ay 7–9)"),
        ("katki_kari_q3", "₺", "Q3 Katkı Kârı  (Ay 7–9)"),
    ]):
        ax = axes[ax_i]
        x  = np.arange(len(firms))
        for i, (sc_lbl, color) in enumerate(scs):
            scd  = q3_df[q3_df["senaryo"] == sc_lbl]
            vals = [scd[scd["firma"] == f][metric].values[0]
                    if len(scd[scd["firma"] == f]) > 0 else 0 for f in firms]
            for xi, val in zip(x + (i - 1) * w, vals):
                _glow(ax, xi, val, w=w - 0.03, color=color)
        ax.set_xticks(x); ax.set_xticklabels(firms, rotation=28, ha="right", fontsize=9, color=TEXT)
        ax.set_title(title, fontsize=12, fontweight="bold", color=TEXT)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.legend(handles=[mpatches.Patch(color=c, label=s) for s, c in scs],
                  framealpha=0, labelcolor=TEXT, fontsize=9)

    fig.suptitle("3. Çeyrek (Q3) Tahmin Senaryoları",
                 fontsize=14, fontweight="bold", color=TEXT, y=1.02)
    fig.tight_layout()
    return _save(fig, "06_q3_senaryolar")


# ─── 7. ROI Matrisi ───────────────────────────────────────────────────────
def plot_roi_matrix(roi_df: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(11, 5))
    _dark(fig, [ax])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}x"))

    firms  = list(roi_df["firma"])
    vals   = list(roi_df["roi"])
    colors = [FIRM_COLORS.get(f, ACCENT) for f in firms]
    y      = np.arange(len(firms))

    for yi, (val, color) in enumerate(zip(vals, colors)):
        ax.barh(yi, val, height=0.5, color=color, alpha=0.92, zorder=3)
        ax.barh(yi, val, height=0.65, color=color, alpha=0.07, zorder=2)
        ax.text(val + 0.04, yi, f"{val:.2f}x", va="center",
                fontsize=10, fontweight="bold", color=color)

    ax.axvline(x=1, color=AMBER, linestyle="--", linewidth=1.6,
               label="1x — başa baş", zorder=5)
    ax.set_yticks(y); ax.set_yticklabels(firms, fontsize=10, color=TEXT)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}x"))
    ax.set_title("Kanal ROI  ·  Katkı Kârı / Toplam Kanal Ödemesi",
                 fontsize=13, fontweight="bold", color=TEXT, pad=12)
    ax.set_xlabel("ROI", fontsize=10)
    ax.legend(framealpha=0, labelcolor=TEXT, fontsize=9)
    fig.tight_layout()
    return _save(fig, "07_roi_matrisi")


# ─── 8. Müşteri Kalitesi ──────────────────────────────────────────────────
def plot_quality_score(quality_df: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(11, 5))
    _dark(fig, [ax])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}"))

    firms  = list(quality_df["firma"])
    scores = list(quality_df["kalite_skoru"])
    colors = [FIRM_COLORS.get(f, ACCENT) for f in firms]
    x      = np.arange(len(firms))

    for xi, (val, color) in enumerate(zip(scores, colors)):
        ax.bar(xi, val, width=0.6, color=color, alpha=0.92, zorder=3)
        ax.bar(xi, val, width=0.76, color=color, alpha=0.07, zorder=2)
        ax.text(xi, val + 1.2, f"{val:.0f}", ha="center", va="bottom",
                fontsize=12, color=color, fontweight="bold")

    ax.axhline(y=60, color=AMBER, linestyle="--", linewidth=1.4,
               label="Min. kabul (60)", zorder=5)
    ax.set_ylim(0, 112)
    ax.set_xticks(x); ax.set_xticklabels(firms, fontsize=10, color=TEXT)
    ax.set_title("Müşteri Kalitesi Bileşik Skoru  (0–100)",
                 fontsize=13, fontweight="bold", color=TEXT, pad=12)
    ax.set_ylabel("Skor", fontsize=10)
    ax.legend(framealpha=0, labelcolor=TEXT, fontsize=9)
    fig.tight_layout()
    return _save(fig, "08_musteri_kalitesi")


# ─── 9. Tahmin Trendi — 6 firma ───────────────────────────────────────────
def plot_forecast_trend(full_year_baz: pd.DataFrame) -> str:
    firms = sorted(full_year_baz["firma"].unique())
    fig, axes = plt.subplots(2, 3, figsize=(18, 9))
    _dark(fig, axes.flatten())

    for ax, firma in zip(axes.flatten(), firms):
        fdf      = full_year_baz[full_year_baz["firma"] == firma].sort_values("ay")
        actual   = fdf[fdf["tip"] == "actual"]
        forecast = fdf[fdf["tip"].str.startswith("forecast")]
        color    = FIRM_COLORS.get(firma, ACCENT)

        ax.plot(actual["ay"], actual["net_satis"],
                "o-", color=color, linewidth=2.4, zorder=4,
                markersize=7, markerfacecolor=BG, markeredgewidth=2,
                label="Gerçekleşen")

        if len(forecast) > 0:
            # Güven bandı (tahmin belirsizliği)
            fc_vals = forecast["net_satis"].values
            band_lo = fc_vals * 0.90
            band_hi = fc_vals * 1.10
            ax.fill_between(forecast["ay"], band_lo, band_hi,
                            alpha=0.12, color=color, zorder=1)
            ax.plot(forecast["ay"], fc_vals,
                    "s--", color=color, linewidth=1.8, alpha=0.7, zorder=3,
                    markersize=5, markerfacecolor=BG, markeredgewidth=1.5,
                    label="Tahmin (Baz)")

        ax.axvline(x=5.5, color=TEXT2, linestyle=":", linewidth=1, zorder=2)
        ax.set_facecolor(SURFACE)

        # Ay 5.5 etiketi
        ymax = ax.get_ylim()[1]
        ax.text(5.7, ymax * 0.95, "tahmin →", fontsize=7,
                color=TEXT2, va="top")

        ax.set_title(firma, fontsize=11, fontweight="bold", color=color)
        ax.set_xlabel("Ay", fontsize=8)
        ax.set_ylabel("Net Satış (₺)", fontsize=8)
        ax.set_xticks(range(1, 13))
        ax.legend(framealpha=0, labelcolor=TEXT2, fontsize=7)

    fig.suptitle("Firma Bazlı Yıllık Trend + Baz Senaryo Tahmini  ·  ±%10 Güven Bandı",
                 fontsize=14, fontweight="bold", color=TEXT, y=1.01)
    fig.tight_layout()
    return _save(fig, "09_tahmin_trendi")
