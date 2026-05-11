"""
Senaryo ve duyarlılık analizi.

Her firmanın katkı kârının hangi parametreye ne kadar duyarlı olduğunu ölçer:
  - Satış hacmi ±%10, ±%20
  - İade oranı ±%2 puan
  - Ürün maliyeti ±%5 puan
  - Ödül oranı ±%1 puan
"""

import pandas as pd
import numpy as np
from models.commission import enrich_dataframe
from config.settings import FIRM_PROFILES


def sensitivity_grid(actual_df: pd.DataFrame) -> pd.DataFrame:
    """Firma bazlı 1-at-a-time duyarlılık tablosu."""
    perturbations = {
        "satis_-20%":    {"satis": 0.80, "iade": 1.00, "maliyet": 1.00},
        "satis_-10%":    {"satis": 0.90, "iade": 1.00, "maliyet": 1.00},
        "baz":           {"satis": 1.00, "iade": 1.00, "maliyet": 1.00},
        "satis_+10%":    {"satis": 1.10, "iade": 1.00, "maliyet": 1.00},
        "satis_+20%":    {"satis": 1.20, "iade": 1.00, "maliyet": 1.00},
        "iade_+2pp":     {"satis": 1.00, "iade": 1.30, "maliyet": 1.00},
        "iade_-2pp":     {"satis": 1.00, "iade": 0.70, "maliyet": 1.00},
        "maliyet_+5pp":  {"satis": 1.00, "iade": 1.00, "maliyet": 1.10},
        "maliyet_-5pp":  {"satis": 1.00, "iade": 1.00, "maliyet": 0.90},
    }

    rows = []
    for label, p in perturbations.items():
        df_copy = actual_df.copy()
        df_copy["net_satis"]               *= p["satis"]
        df_copy["iade"]                    *= p["iade"]
        df_copy["urun_maliyeti"]           *= p["maliyet"]
        df_copy["kanal_degisken_maliyeti"] *= p["maliyet"]
        df_copy["komisyon"]                 = df_copy["net_satis"] * 0.10

        enriched = enrich_dataframe(df_copy)

        for firma, grp in enriched.groupby("firma"):
            rows.append({
                "firma": firma,
                "pertürbasyon": label,
                "net_satis": grp["net_satis"].sum(),
                "katki_kari": grp["katki_kari"].sum(),
                "katki_marji": grp["katki_kari"].sum() / grp["net_satis"].sum() if grp["net_satis"].sum() > 0 else 0,
            })

    result = pd.DataFrame(rows).round(2)
    return result


def tornado_data(sensitivity_df: pd.DataFrame, firma: str) -> pd.DataFrame:
    """Tornado chart için: baz katkı kârından sapma miktarı."""
    fdf = sensitivity_df[sensitivity_df["firma"] == firma]
    baz_kar = fdf[fdf["pertürbasyon"] == "baz"]["katki_kari"].values[0]

    pairs = [
        ("satis_-20%",   "satis_+20%",   "Satış ±%20"),
        ("satis_-10%",   "satis_+10%",   "Satış ±%10"),
        ("iade_+2pp",    "iade_-2pp",    "İade ±2pp"),
        ("maliyet_+5pp", "maliyet_-5pp", "Maliyet ±5pp"),
    ]

    records = []
    for low_lbl, high_lbl, name in pairs:
        low  = fdf[fdf["pertürbasyon"] == low_lbl]["katki_kari"].values[0]
        high = fdf[fdf["pertürbasyon"] == high_lbl]["katki_kari"].values[0]
        records.append({
            "faktör": name,
            "dusuk_senaryo": low - baz_kar,
            "yuksek_senaryo": high - baz_kar,
            "etki_araligi": abs(high - low),
        })

    return pd.DataFrame(records).sort_values("etki_araligi", ascending=True)
