"""
Komisyon Kârlılık Sistemi — Ana çalıştırıcı.

Kullanım:
    python main.py

Çıktılar:
    output/actual_data.csv
    output/rapor.html
    output/*.png  (9 grafik)
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from pathlib import Path

from data.generator import generate_all_firms
from models.commission import enrich_dataframe
from models.profitability import (
    contribution_margin_summary,
    break_even_analysis,
    roi_analysis,
    waterfall_data,
    customer_quality_score,
)
from models.forecasting import (
    generate_all_forecasts,
    build_full_year,
    q3_summary,
    yearend_summary,
)
from visualization.charts import (
    plot_monthly_sales,
    plot_contribution_margin,
    plot_effective_payment,
    plot_waterfall,
    plot_yearend_scenarios,
    plot_q3_scenarios,
    plot_roi_matrix,
    plot_quality_score,
    plot_forecast_trend,
)
from reports.report_generator import generate_report

Path("output").mkdir(exist_ok=True)


def main():
    print("=" * 60)
    print("  KOMİSYON KÂRLILIK SİSTEMİ")
    print("  1 Yıllık Sözleşme | %10 Komisyon | 5 Skala")
    print("  5. Ay Gerçekleşen + Q3 & Yıl Sonu Tahmin")
    print("=" * 60)

    # ─── 1. Veri Üretimi ─────────────────────────────────────────
    print("\n[1/7] Sentetik veri üretiliyor (Ay 1-5)...")
    actual_df = generate_all_firms()
    actual_df = enrich_dataframe(actual_df, model="incremental")
    actual_df.to_csv("output/actual_data.csv", index=False)
    print(f"      {len(actual_df)} satır gerçekleşen veri oluşturuldu.")

    # ─── 2. Kârlılık Analizi ─────────────────────────────────────
    print("\n[2/7] Kârlılık analizi hesaplanıyor...")
    summary_df = contribution_margin_summary(actual_df)
    be_df      = break_even_analysis(actual_df)
    roi_df     = roi_analysis(actual_df)
    quality_df = customer_quality_score(actual_df)

    summary_df.to_csv("output/katki_marji_ozet.csv", index=False)
    be_df.to_csv("output/breakeven.csv", index=False)
    roi_df.to_csv("output/roi.csv", index=False)
    quality_df.to_csv("output/musteri_kalitesi.csv", index=False)

    print("\n  📊 Katkı Marjı Özeti:")
    print(summary_df[["firma", "net_satis_toplam", "katki_kari_toplam",
                       "katki_marji", "efektif_odeme_orani"]].to_string(index=False))

    # ─── 3. Tahmin Modelleri ──────────────────────────────────────
    print("\n[3/7] Tahmin modelleri çalışıyor (Ay 6-12, 3 senaryo)...")
    forecasts   = generate_all_forecasts(actual_df)
    full_year   = build_full_year(actual_df, forecasts)
    q3_df       = q3_summary(full_year)
    yearend_df  = yearend_summary(full_year)

    q3_df.to_csv("output/q3_tahmin.csv", index=False)
    yearend_df.to_csv("output/yilsonu_tahmin.csv", index=False)

    print("\n  🔮 Yıl Sonu Kümülatif Katkı Kârı (Baz Senaryo):")
    baz_ye = yearend_df[yearend_df["senaryo"] == "Baz"][["firma", "net_satis_yil", "katki_kari_yil", "katki_marji_yil"]]
    print(baz_ye.to_string(index=False))

    # ─── 4. Grafikler ─────────────────────────────────────────────
    print("\n[4/7] Grafikler oluşturuluyor...")
    chart_paths = []
    chart_paths.append(plot_monthly_sales(actual_df))
    chart_paths.append(plot_contribution_margin(summary_df))
    chart_paths.append(plot_effective_payment(summary_df))

    for firma in actual_df["firma"].unique():
        wf = waterfall_data(actual_df, firma)
        chart_paths.append(plot_waterfall(wf, firma))

    chart_paths.append(plot_yearend_scenarios(yearend_df))
    chart_paths.append(plot_q3_scenarios(q3_df))
    chart_paths.append(plot_roi_matrix(roi_df))
    chart_paths.append(plot_quality_score(quality_df))
    chart_paths.append(plot_forecast_trend(full_year["baz"]))
    print(f"      {len(chart_paths)} grafik oluşturuldu.")

    # ─── 5. HTML Rapor ────────────────────────────────────────────
    print("\n[5/7] HTML raporu oluşturuluyor...")
    report_path = generate_report(
        actual_df, summary_df, be_df, roi_df,
        q3_df, yearend_df, quality_df, chart_paths
    )
    print(f"      Rapor: {report_path}")

    # ─── 6. Karar Özeti ───────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  KARAR ÖZETİ")
    print("=" * 60)

    best_firma  = summary_df.nlargest(1, "katki_marji")
    worst_firma = summary_df.nsmallest(1, "katki_marji")

    print(f"\n  🏆 En Karlı Firma : {best_firma['firma'].values[0]}")
    print(f"     Katkı Marjı   : %{best_firma['katki_marji'].values[0]*100:.1f}")
    print(f"     ROI           : {roi_df[roi_df['firma']==best_firma['firma'].values[0]]['roi'].values[0]:.2f}x")

    print(f"\n  ⚠️  En Riskli Firma: {worst_firma['firma'].values[0]}")
    print(f"     Katkı Marjı   : %{worst_firma['katki_marji'].values[0]*100:.1f}")

    guardrail_violations = summary_df[summary_df["guardrail_asim"] == True]
    if not guardrail_violations.empty:
        print(f"\n  🚨 Guardrail Aşımı: {', '.join(guardrail_violations['firma'].tolist())}")
    else:
        print("\n  ✅ Guardrail: Tüm firmalar sınır içinde.")

    print("\n  📁 Tüm çıktılar: output/ klasöründe")
    print(f"  🌐 Raporu açmak için: open {report_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
