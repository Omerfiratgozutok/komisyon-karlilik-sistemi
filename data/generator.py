"""
Sentetik satış verisi üretici.
6 firma için 12 aylık gerçekçi veri oluşturur.
Ay 1-5: gerçekleşen (actual), Ay 6-12: boş (tahmin modeli dolduracak).
"""

import numpy as np
import pandas as pd
from config.settings import FIRM_PROFILES, CURRENT_MONTH

np.random.seed(42)


def generate_monthly_data(firm_name: str, profile: dict, months: int = CURRENT_MONTH) -> pd.DataFrame:
    records = []
    base = profile["aylik_gross_satis_ortalama"]
    std  = profile["gross_satis_std"]
    trend = profile["buyume_trendi"]
    seasonality = profile["sezonsellik"]

    for m in range(1, months + 1):
        season_factor = seasonality[m - 1]
        trend_factor  = (1 + trend) ** (m - 1)
        gross_satis   = max(0, np.random.normal(base * season_factor * trend_factor, std))

        iade         = gross_satis * np.random.uniform(
            profile["iade_orani"] * 0.8, profile["iade_orani"] * 1.2
        )
        iskonto      = gross_satis * np.random.uniform(
            profile["iskonto_orani"] * 0.8, profile["iskonto_orani"] * 1.2
        )
        net_satis    = gross_satis - iade - iskonto

        komisyon     = net_satis * 0.10
        urun_maliyeti = net_satis * profile["birim_degisken_maliyet_orani"]
        kanal_maliyeti = net_satis * profile["kanal_degisken_maliyet_orani"]

        records.append({
            "firma": firm_name,
            "ay": m,
            "tip": "actual",
            "gross_satis": round(gross_satis, 2),
            "iade": round(iade, 2),
            "iskonto": round(iskonto, 2),
            "net_satis": round(net_satis, 2),
            "komisyon": round(komisyon, 2),
            "urun_maliyeti": round(urun_maliyeti, 2),
            "kanal_degisken_maliyeti": round(kanal_maliyeti, 2),
            "iade_orani_gercek": round(iade / gross_satis, 4) if gross_satis > 0 else 0,
            "yeni_musteri_orani": profile["yeni_musteri_orani"],
            "tahsilat_gecikme_gun": profile["tahsilat_gecikme_gun"],
            "skala": profile["skala"],
        })

    return pd.DataFrame(records)


def generate_all_firms() -> pd.DataFrame:
    frames = []
    for firm, profile in FIRM_PROFILES.items():
        df = generate_monthly_data(firm, profile, months=CURRENT_MONTH)
        frames.append(df)
    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv("output/actual_data.csv", index=False)
    return combined


if __name__ == "__main__":
    df = generate_all_firms()
    print(df.groupby("firma")[["net_satis", "komisyon"]].sum().round(0))
