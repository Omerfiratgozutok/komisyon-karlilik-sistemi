"""
Tahmin modelleri — Ay 5 gerçekleşen veriden Ay 6-12 tahmini.

Kullanılan teknikler:
  - Trend + sezonsellik dekompozisyonu (statsmodels ExponentialSmoothing)
  - Linear trend extrapolation (sklearn)
  - 3 senaryo: kötümser / baz / iyimser

Çıktı:
  - Q3 tahmini (Ay 7-9)
  - Yıl sonu tahmini (Ay 1-12 kümülatif)
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from config.settings import FIRM_PROFILES, SCENARIOS, CURRENT_MONTH, CONTRACT_MONTHS
from models.commission import enrich_dataframe


def _linear_trend_forecast(actuals: list[float], n_future: int) -> list[float]:
    """Basit lineer trend extrapolasyon."""
    X = np.arange(len(actuals)).reshape(-1, 1)
    y = np.array(actuals)
    reg = LinearRegression().fit(X, y)
    X_fut = np.arange(len(actuals), len(actuals) + n_future).reshape(-1, 1)
    preds = reg.predict(X_fut)
    return [max(0, p) for p in preds]


def _apply_seasonality(base_values: list[float], firm_name: str, start_month: int) -> list[float]:
    """Firm'e özgü sezonsellik katsayılarını uygular."""
    seasonality = FIRM_PROFILES[firm_name]["sezonsellik"]
    # Ay 1-5 ortalamasından normalize et
    base_season_avg = np.mean(seasonality[:CURRENT_MONTH])
    result = []
    for i, val in enumerate(base_values):
        month_idx = start_month - 1 + i  # 0-indexed
        if month_idx < 12:
            factor = seasonality[month_idx] / base_season_avg
        else:
            factor = 1.0
        result.append(val * factor)
    return result


def forecast_firm(firm_name: str, actual_df: pd.DataFrame, scenario: str = "baz") -> pd.DataFrame:
    """Bir firma için Ay 6-12 tahmini üretir."""
    sc = SCENARIOS[scenario]
    firm_data = actual_df[actual_df["firma"] == firm_name].sort_values("ay")
    actuals_net = firm_data["net_satis"].tolist()

    n_future = CONTRACT_MONTHS - CURRENT_MONTH
    future_months = list(range(CURRENT_MONTH + 1, CONTRACT_MONTHS + 1))

    # Trend tahmini
    trend_preds = _linear_trend_forecast(actuals_net, n_future)

    # Sezonsellik uygula
    seasonal_preds = _apply_seasonality(trend_preds, firm_name, CURRENT_MONTH + 1)

    profile = FIRM_PROFILES[firm_name]
    records = []
    for i, (month, pred_net) in enumerate(zip(future_months, seasonal_preds)):
        # Senaryo çarpanı uygula
        net_satis = pred_net * sc["satis_carpani"]

        # Gross satış geriye hesapla
        iade_orani   = profile["iade_orani"] * sc["iade_carpani"]
        iskonto_orani = profile["iskonto_orani"]
        gross_satis  = net_satis / (1 - iade_orani - iskonto_orani)
        iade         = gross_satis * iade_orani
        iskonto      = gross_satis * iskonto_orani

        urun_maliyeti  = net_satis * profile["birim_degisken_maliyet_orani"] * sc["maliyet_carpani"]
        kanal_maliyeti = net_satis * profile["kanal_degisken_maliyet_orani"] * sc["maliyet_carpani"]

        records.append({
            "firma": firm_name,
            "ay": month,
            "tip": f"forecast_{scenario}",
            "senaryo": SCENARIOS[scenario]["label"],
            "gross_satis": round(gross_satis, 2),
            "iade": round(iade, 2),
            "iskonto": round(iskonto, 2),
            "net_satis": round(net_satis, 2),
            "komisyon": round(net_satis * 0.10, 2),
            "urun_maliyeti": round(urun_maliyeti, 2),
            "kanal_degisken_maliyeti": round(kanal_maliyeti, 2),
            "iade_orani_gercek": round(iade_orani, 4),
            "yeni_musteri_orani": profile["yeni_musteri_orani"],
            "tahsilat_gecikme_gun": profile["tahsilat_gecikme_gun"],
            "skala": profile["skala"],
            "birim_degisken_maliyet_orani": profile["birim_degisken_maliyet_orani"],
            "kanal_degisken_maliyet_orani": profile["kanal_degisken_maliyet_orani"],
        })

    return pd.DataFrame(records)


def generate_all_forecasts(actual_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Tüm firmalar ve 3 senaryo için tahmin DataFrame'leri üretir."""
    results = {}
    firms = actual_df["firma"].unique()

    for scenario in SCENARIOS:
        frames = []
        for firm in firms:
            fc = forecast_firm(firm, actual_df, scenario=scenario)
            fc_enriched = enrich_dataframe(fc, model="incremental")
            frames.append(fc_enriched)
        results[scenario] = pd.concat(frames, ignore_index=True)

    return results


def build_full_year(actual_df: pd.DataFrame, forecasts: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """
    Gerçekleşen (Ay 1-5) + Tahmin (Ay 6-12) birleştirme.
    Her senaryo için tam yıl DataFrame'i döner.
    """
    # Ortak sütun kümesini belirle
    common_cols = [
        "firma", "ay", "tip", "net_satis", "gross_satis", "iade", "iskonto",
        "urun_maliyeti", "kanal_degisken_maliyeti", "skala",
        "komisyon", "satis_odulu", "katki_kari", "katki_marji",
        "efektif_odeme_orani", "iade_orani_gercek", "tahsilat_gecikme_gun",
        "yeni_musteri_orani",
    ]

    def _align(df):
        for col in common_cols:
            if col not in df.columns:
                df = df.copy()
                df[col] = None
        return df[common_cols]

    full = {}
    for scenario, fc_df in forecasts.items():
        combined = pd.concat([_align(actual_df), _align(fc_df)], ignore_index=True)
        combined = combined.sort_values(["firma", "ay"]).reset_index(drop=True)
        full[scenario] = combined
    return full


def q3_summary(full_year: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Q3 (Ay 7-9) tahmin özeti — firma x senaryo."""
    rows = []
    for scenario, df in full_year.items():
        q3 = df[df["ay"].between(7, 9)]
        grp = q3.groupby("firma").agg(
            net_satis_q3=("net_satis", "sum"),
            katki_kari_q3=("katki_kari", "sum"),
            komisyon_q3=("komisyon", "sum"),
            satis_odulu_q3=("satis_odulu", "sum"),
        ).reset_index()
        grp["senaryo"] = SCENARIOS[scenario]["label"]
        grp["katki_marji_q3"] = (grp["katki_kari_q3"] / grp["net_satis_q3"]).round(4)
        rows.append(grp)
    return pd.concat(rows, ignore_index=True).round(2)


def yearend_summary(full_year: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Yıl sonu kümülatif özeti — firma x senaryo."""
    rows = []
    for scenario, df in full_year.items():
        grp = df.groupby("firma").agg(
            net_satis_yil=("net_satis", "sum"),
            katki_kari_yil=("katki_kari", "sum"),
            komisyon_yil=("komisyon", "sum"),
            satis_odulu_yil=("satis_odulu", "sum"),
        ).reset_index()
        grp["senaryo"] = SCENARIOS[scenario]["label"]
        grp["katki_marji_yil"] = (grp["katki_kari_yil"] / grp["net_satis_yil"]).round(4)
        grp["efektif_odeme"] = (
            (grp["komisyon_yil"] + grp["satis_odulu_yil"]) / grp["net_satis_yil"]
        ).round(4)
        rows.append(grp)
    return pd.concat(rows, ignore_index=True).round(2)
