"""
Kârlılık analiz modülleri.

İçerik:
  - Katkı marjı özeti
  - Break-even hesabı (sabit maliyet varsa)
  - ROI hesabı
  - Waterfall verileri
  - Cohort / müşteri kalitesi skoru
"""

import pandas as pd
import numpy as np
from config.settings import GROSS_MARGIN_RATE, VARIABLE_OPS_COST_RATE, CONTRACT_COMMISSION_RATE, MAX_REWARD_RATE


# ─── Katkı Marjı Özeti ────────────────────────────────────────────────────
def contribution_margin_summary(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby("firma").agg(
        gross_satis_toplam=("gross_satis", "sum"),
        iade_toplam=("iade", "sum"),
        iskonto_toplam=("iskonto", "sum"),
        net_satis_toplam=("net_satis", "sum"),
        komisyon_toplam=("komisyon", "sum"),
        satis_odulu_toplam=("satis_odulu", "sum"),
        urun_maliyeti_toplam=("urun_maliyeti", "sum"),
        kanal_maliyeti_toplam=("kanal_degisken_maliyeti", "sum"),
        katki_kari_toplam=("katki_kari", "sum"),
    ).reset_index()

    grp["iade_orani"] = grp["iade_toplam"] / grp["gross_satis_toplam"]
    grp["katki_marji"] = grp["katki_kari_toplam"] / grp["net_satis_toplam"]
    grp["efektif_odeme_orani"] = (grp["komisyon_toplam"] + grp["satis_odulu_toplam"]) / grp["net_satis_toplam"]
    grp["roi"] = grp["katki_kari_toplam"] / (grp["komisyon_toplam"] + grp["satis_odulu_toplam"])

    # Guardrail: efektif ödeme oranı > %13 uyarısı
    grp["guardrail_asim"] = grp["efektif_odeme_orani"] > MAX_REWARD_RATE + CONTRACT_COMMISSION_RATE

    grp = grp.round(2)
    return grp


# ─── Break-even Analizi ───────────────────────────────────────────────────
FIRMA_SABIT_MALIYET = {
    "Firma_A": 50_000,
    "Firma_B": 30_000,
    "Firma_C": 25_000,
    "Firma_D": 60_000,
    "Firma_E": 35_000,
    "Firma_F": 20_000,
}


def break_even_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Her firma için dönemlik break-even net satış hesabı."""
    summary = contribution_margin_summary(df)
    records = []

    for _, row in summary.iterrows():
        firma = row["firma"]
        sabit = FIRMA_SABIT_MALIYET.get(firma, 0)
        net = row["net_satis_toplam"]

        # Katki marjı oranı (ortalama)
        km_oran = row["katki_marji"]
        be_satis = sabit / km_oran if km_oran > 0 else float("inf")

        records.append({
            "firma": firma,
            "sabit_maliyet": sabit,
            "katki_marji_oran": round(km_oran, 4),
            "breakeven_net_satis": round(be_satis, 2),
            "gercek_net_satis": round(net, 2),
            "breakeven_asim": net > be_satis,
            "guvenlik_marji": round((net - be_satis) / net, 4) if net > 0 else 0,
        })

    return pd.DataFrame(records)


# ─── ROI Analizi ──────────────────────────────────────────────────────────
def roi_analysis(df: pd.DataFrame) -> pd.DataFrame:
    summary = contribution_margin_summary(df)
    summary["roi_formatted"] = summary["roi"].apply(lambda x: f"{x:.2f}x")
    summary["kanal_odemesi"] = summary["komisyon_toplam"] + summary["satis_odulu_toplam"]
    return summary[["firma", "kanal_odemesi", "katki_kari_toplam", "roi", "roi_formatted"]]


# ─── Waterfall Verisi ─────────────────────────────────────────────────────
def waterfall_data(df: pd.DataFrame, firma: str) -> pd.DataFrame:
    fdf = df[df["firma"] == firma].sum(numeric_only=True)

    steps = [
        ("Brüt Satış",              fdf["gross_satis"],                    "bar"),
        ("- İade & İskonto",       -(fdf["iade"] + fdf["iskonto"]),        "waterfall"),
        ("Net Satış",               fdf["net_satis"],                      "total"),
        ("- Ürün Maliyeti",        -fdf["urun_maliyeti"],                  "waterfall"),
        ("- Komisyon (%10)",       -fdf["komisyon"],                       "waterfall"),
        ("- Satış Ödülü",         -fdf["satis_odulu"],                    "waterfall"),
        ("- Kanal Değişken Mal.", -fdf["kanal_degisken_maliyeti"],         "waterfall"),
        ("Katkı Kârı",             fdf["katki_kari"],                      "total"),
    ]

    return pd.DataFrame(steps, columns=["adim", "deger", "tip"])


# ─── Cohort / Müşteri Kalitesi Skoru ─────────────────────────────────────
def customer_quality_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    0-100 arası bileşik müşteri kalitesi skoru.
    Bileşenler: iade oranı (ters), yeni müşteri oranı, tahsilat gecikmesi (ters), katki marjı
    """
    summary = contribution_margin_summary(df)

    firm_extra = df.groupby("firma").agg(
        yeni_musteri_orani=("yeni_musteri_orani", "mean"),
        tahsilat_gecikme=("tahsilat_gecikme_gun", "mean"),
    ).reset_index()

    merged = summary.merge(firm_extra, on="firma")

    def normalize(series, inverse=False):
        mn, mx = series.min(), series.max()
        if mx == mn:
            return pd.Series([50.0] * len(series))
        norm = (series - mn) / (mx - mn)
        return (1 - norm) * 100 if inverse else norm * 100

    merged["skor_katki_marji"]     = normalize(merged["katki_marji"])
    merged["skor_iade"]            = normalize(merged["iade_orani"], inverse=True)
    merged["skor_yeni_musteri"]    = normalize(merged["yeni_musteri_orani"])
    merged["skor_tahsilat"]        = normalize(merged["tahsilat_gecikme"], inverse=True)

    merged["kalite_skoru"] = (
        merged["skor_katki_marji"]  * 0.40 +
        merged["skor_iade"]         * 0.25 +
        merged["skor_yeni_musteri"] * 0.20 +
        merged["skor_tahsilat"]     * 0.15
    ).round(1)

    return merged[["firma", "kalite_skoru", "skor_katki_marji", "skor_iade",
                   "skor_yeni_musteri", "skor_tahsilat"]]
