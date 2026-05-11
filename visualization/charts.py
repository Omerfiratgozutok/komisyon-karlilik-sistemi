"""
Grafik üretici — matplotlib tabanlı, output/ klasörüne PNG kaydeder.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from pathlib import Path
from config.settings import SCENARIOS

COLORS = {
    "Firma_A": "#2980b9",
    "Firma_B": "#27ae60",
    "Firma_C": "#8e44ad",
    "Firma_D": "#e74c3c",
    "Firma_E": "#f39c12",
    "Firma_F": "#7f8c8d",
}
SCENARIO_COLORS = {s: v["color"] for s, v in SCENARIOS.items()}

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)


def _save(fig, name: str):
    path = OUTPUT / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(path)


# ─── 1. Aylık Net Satış Trendi (gerçekleşen) ──────────────────────────────
def plot_monthly_sales(actual_df: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(12, 5))
    for firma, grp in actual_df.groupby("firma"):
        grp = grp.sort_values("ay")
        ax.plot(grp["ay"], grp["net_satis"] / 1000, marker="o", label=firma,
                color=COLORS.get(firma), linewidth=2)
    ax.set_title("Aylık Net Satış — Ay 1-5 (Gerçekleşen)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Ay")
    ax.set_ylabel("Net Satış (bin TL)")
    ax.set_xticks(range(1, 6))
    ax.legend(loc="upper left", ncol=2)
    ax.grid(axis="y", alpha=0.3)
    return _save(fig, "01_aylik_net_satis")


# ─── 2. Katkı Marjı Karşılaştırma ─────────────────────────────────────────
def plot_contribution_margin(summary_df: pd.DataFrame) -> str:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    firms = summary_df["firma"]
    colors = [COLORS.get(f, "#333") for f in firms]

    # Sol: katkı kârı
    ax = axes[0]
    bars = ax.bar(firms, summary_df["katki_kari_toplam"] / 1000, color=colors, edgecolor="white")
    ax.set_title("Katkı Kârı (bin TL)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Katkı Kârı (bin TL)")
    ax.tick_params(axis="x", rotation=30)
    for bar, val in zip(bars, summary_df["katki_kari_toplam"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{val/1000:,.0f}", ha="center", va="bottom", fontsize=9)

    # Sağ: katkı marjı %
    ax = axes[1]
    bars = ax.bar(firms, summary_df["katki_marji"] * 100, color=colors, edgecolor="white")
    ax.axhline(y=15, color="red", linestyle="--", linewidth=1.5, label="Hedef %15")
    ax.set_title("Katkı Marjı (%)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Katkı Marjı %")
    ax.tick_params(axis="x", rotation=30)
    ax.legend()
    for bar, val in zip(bars, summary_df["katki_marji"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{val*100:.1f}%", ha="center", va="bottom", fontsize=9)

    fig.suptitle("Firma Bazlı Katkı Kârı Analizi (Ay 1-5)", fontsize=14, fontweight="bold")
    fig.tight_layout()
    return _save(fig, "02_katki_marji")


# ─── 3. Efektif Ödeme Oranı & Guardrail ──────────────────────────────────
def plot_effective_payment(summary_df: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(10, 5))
    from config.settings import MAX_REWARD_RATE, CONTRACT_COMMISSION_RATE
    threshold = (MAX_REWARD_RATE + CONTRACT_COMMISSION_RATE) * 100

    x = np.arange(len(summary_df))
    colors = ["#e74c3c" if v * 100 > threshold else "#2980b9"
              for v in summary_df["efektif_odeme_orani"]]
    bars = ax.bar(x, summary_df["efektif_odeme_orani"] * 100, color=colors, edgecolor="white")
    ax.axhline(y=threshold, color="red", linestyle="--", linewidth=2,
               label=f"Guardrail %{threshold:.0f} (komisyon+maks ödül)")
    ax.set_xticks(x)
    ax.set_xticklabels(summary_df["firma"], rotation=30)
    ax.set_title("Efektif Ödeme Oranı (Komisyon + Ödül) / Net Satış", fontsize=13, fontweight="bold")
    ax.set_ylabel("Efektif Ödeme Oranı %")
    ax.legend()
    for bar, val in zip(bars, summary_df["efektif_odeme_orani"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                f"{val*100:.1f}%", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    return _save(fig, "03_efektif_odeme_orani")


# ─── 4. Waterfall Chart ────────────────────────────────────────────────────
def plot_waterfall(waterfall_df: pd.DataFrame, firma: str) -> str:
    fig, ax = plt.subplots(figsize=(12, 6))
    steps = waterfall_df["adim"].tolist()
    values = waterfall_df["deger"].tolist()
    types  = waterfall_df["tip"].tolist()

    running = 0
    bottoms = []
    heights = []
    bar_colors = []

    for i, (v, t) in enumerate(zip(values, types)):
        if t == "bar" or t == "total":
            bottoms.append(0)
            heights.append(v)
            bar_colors.append("#2980b9" if v > 0 else "#e74c3c")
            running = v
        else:  # waterfall step
            if v >= 0:
                bottoms.append(running)
                heights.append(v)
                bar_colors.append("#27ae60")
            else:
                bottoms.append(running + v)
                heights.append(-v)
                bar_colors.append("#e74c3c")
            running += v

    x = np.arange(len(steps))
    bars = ax.bar(x, heights, bottom=bottoms, color=bar_colors, edgecolor="white", width=0.6)

    for i, (bar, v) in enumerate(zip(bars, values)):
        ypos = bar.get_y() + bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, ypos + max(heights) * 0.01,
                f"{v/1000:+,.0f}K", ha="center", va="bottom", fontsize=8, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(steps, rotation=30, ha="right")
    ax.set_title(f"Waterfall Analizi — {firma} (Ay 1-5 Kümülatif)", fontsize=13, fontweight="bold")
    ax.set_ylabel("TL (bin)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/1000:,.0f}K"))
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return _save(fig, f"04_waterfall_{firma}")


# ─── 5. Yıl Sonu Senaryo Karşılaştırması ─────────────────────────────────
def plot_yearend_scenarios(yearend_df: pd.DataFrame) -> str:
    firms = yearend_df["firma"].unique()
    scenarios = ["Kötümser", "Baz", "İyimser"]
    sc_colors = ["#e74c3c", "#3498db", "#2ecc71"]

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for ax_idx, (metric, ylabel, title) in enumerate([
        ("net_satis_yil", "Net Satış (bin TL)", "Yıl Sonu Net Satış Tahmini"),
        ("katki_kari_yil", "Katkı Kârı (bin TL)", "Yıl Sonu Katkı Kârı Tahmini"),
    ]):
        ax = axes[ax_idx]
        x = np.arange(len(firms))
        width = 0.25

        for i, (sc_label, color) in enumerate(zip(scenarios, sc_colors)):
            sc_data = yearend_df[yearend_df["senaryo"] == sc_label]
            vals = [sc_data[sc_data["firma"] == f][metric].values[0] / 1000
                    if len(sc_data[sc_data["firma"] == f]) > 0 else 0
                    for f in firms]
            bars = ax.bar(x + (i - 1) * width, vals, width, label=sc_label, color=color, alpha=0.85)

        ax.set_xticks(x)
        ax.set_xticklabels(firms, rotation=30)
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.set_ylabel(ylabel)
        ax.legend()
        ax.grid(axis="y", alpha=0.3)

    fig.suptitle("Yıl Sonu Tahmin Senaryoları (Ay 1-12 Kümülatif)", fontsize=14, fontweight="bold")
    fig.tight_layout()
    return _save(fig, "05_yilsonu_senaryolar")


# ─── 6. Q3 Senaryo Karşılaştırması ────────────────────────────────────────
def plot_q3_scenarios(q3_df: pd.DataFrame) -> str:
    firms = q3_df["firma"].unique()
    scenarios = ["Kötümser", "Baz", "İyimser"]
    sc_colors = ["#e74c3c", "#3498db", "#2ecc71"]

    fig, axes = plt.subplots(1, 2, figsize=(16, 5))

    for ax_idx, (metric, ylabel, title) in enumerate([
        ("net_satis_q3", "Net Satış (bin TL)", "Q3 Net Satış Tahmini (Ay 7-9)"),
        ("katki_kari_q3", "Katkı Kârı (bin TL)", "Q3 Katkı Kârı Tahmini (Ay 7-9)"),
    ]):
        ax = axes[ax_idx]
        x = np.arange(len(firms))
        width = 0.25

        for i, (sc_label, color) in enumerate(zip(scenarios, sc_colors)):
            sc_data = q3_df[q3_df["senaryo"] == sc_label]
            vals = [sc_data[sc_data["firma"] == f][metric].values[0] / 1000
                    if len(sc_data[sc_data["firma"] == f]) > 0 else 0
                    for f in firms]
            ax.bar(x + (i - 1) * width, vals, width, label=sc_label, color=color, alpha=0.85)

        ax.set_xticks(x)
        ax.set_xticklabels(firms, rotation=30)
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.set_ylabel(ylabel)
        ax.legend()
        ax.grid(axis="y", alpha=0.3)

    fig.suptitle("3. Çeyrek (Q3) Tahmin Senaryoları", fontsize=14, fontweight="bold")
    fig.tight_layout()
    return _save(fig, "06_q3_senaryolar")


# ─── 7. ROI Matrisi ────────────────────────────────────────────────────────
def plot_roi_matrix(roi_df: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(10, 5))
    firms = roi_df["firma"]
    colors = [COLORS.get(f, "#333") for f in firms]

    bars = ax.barh(firms, roi_df["roi"], color=colors, edgecolor="white")
    ax.axvline(x=1, color="red", linestyle="--", linewidth=1.5, label="ROI = 1x (başa baş)")
    ax.set_title("Kanal ROI'si — Katkı Kârı / Toplam Kanal Ödemesi", fontsize=13, fontweight="bold")
    ax.set_xlabel("ROI (x)")
    ax.legend()
    for bar, val in zip(bars, roi_df["roi"]):
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height() / 2,
                f"{val:.2f}x", va="center", fontsize=10, fontweight="bold")
    fig.tight_layout()
    return _save(fig, "07_roi_matrisi")


# ─── 8. Müşteri Kalitesi Skoru ─────────────────────────────────────────────
def plot_quality_score(quality_df: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(10, 5))
    firms = quality_df["firma"]
    scores = quality_df["kalite_skoru"]
    colors = [COLORS.get(f, "#333") for f in firms]

    bars = ax.bar(firms, scores, color=colors, edgecolor="white")
    ax.axhline(y=60, color="orange", linestyle="--", linewidth=1.5, label="Minimum kabul eşiği (60)")
    ax.set_ylim(0, 100)
    ax.set_title("Firma Müşteri Kalitesi Bileşik Skoru (0-100)", fontsize=13, fontweight="bold")
    ax.set_ylabel("Kalite Skoru")
    ax.legend()
    for bar, val in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{val:.0f}", ha="center", va="bottom", fontsize=11, fontweight="bold")
    fig.tight_layout()
    return _save(fig, "08_musteri_kalitesi")


# ─── 9. Tahmin Trendi — Firma bazlı tam yıl ───────────────────────────────
def plot_forecast_trend(full_year_baz: pd.DataFrame) -> str:
    firms = sorted(full_year_baz["firma"].unique())
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes_flat = axes.flatten()

    for ax, firma in zip(axes_flat, firms):
        fdf = full_year_baz[full_year_baz["firma"] == firma].sort_values("ay")
        actual = fdf[fdf["tip"] == "actual"]
        forecast = fdf[fdf["tip"].str.startswith("forecast")]

        ax.plot(actual["ay"], actual["net_satis"] / 1000, "o-",
                color=COLORS.get(firma, "#333"), linewidth=2, label="Gerçekleşen")
        ax.plot(forecast["ay"], forecast["net_satis"] / 1000, "s--",
                color=COLORS.get(firma, "#333"), linewidth=2, alpha=0.6, label="Tahmin (Baz)")
        ax.axvline(x=5.5, color="gray", linestyle=":", linewidth=1.5, label="Tahmin başlangıcı")
        ax.set_title(firma, fontsize=11, fontweight="bold")
        ax.set_xlabel("Ay")
        ax.set_ylabel("Net Satış (bin TL)")
        ax.set_xticks(range(1, 13))
        ax.legend(fontsize=7)
        ax.grid(alpha=0.3)

    fig.suptitle("Firma Bazlı Yıllık Net Satış Trendi + Tahmin (Baz Senaryo)",
                 fontsize=14, fontweight="bold")
    fig.tight_layout()
    return _save(fig, "09_tahmin_trendi")
