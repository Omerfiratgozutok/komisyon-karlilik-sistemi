"""
HTML rapor üretici.
Tüm analiz sonuçlarını tek, interaktif bir HTML dosyasında birleştirir.
"""

import pandas as pd
from pathlib import Path
from datetime import date

OUTPUT = Path("output")


def _fmt(val, kind="tl"):
    if kind == "tl":
        return f"₺{val:,.0f}"
    elif kind == "pct":
        return f"{val*100:.1f}%"
    elif kind == "x":
        return f"{val:.2f}x"
    return str(val)


def _table_html(df: pd.DataFrame, col_formats: dict = None) -> str:
    col_formats = col_formats or {}
    rows = ""
    for _, r in df.iterrows():
        cells = ""
        for col in df.columns:
            fmt = col_formats.get(col, "")
            val = r[col]
            if fmt == "tl":
                cell = _fmt(val, "tl") if isinstance(val, (int, float)) else val
            elif fmt == "pct":
                cell = _fmt(val, "pct") if isinstance(val, (int, float)) else val
            elif fmt == "x":
                cell = _fmt(val, "x") if isinstance(val, (int, float)) else val
            elif fmt == "bool":
                cell = "⚠️ Aşım" if val else "✅ OK"
            else:
                cell = val
            cells += f"<td>{cell}</td>"
        rows += f"<tr>{cells}</tr>"

    headers = "".join(f"<th>{c}</th>" for c in df.columns)
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table>"


def _img(name: str, caption: str = "") -> str:
    return (
        f'<figure>'
        f'<img src="{name}.png" alt="{caption}" '
        f'style="max-width:100%;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.15);">'
        f'<figcaption>{caption}</figcaption></figure>'
    )


def generate_report(
    actual_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    be_df: pd.DataFrame,
    roi_df: pd.DataFrame,
    q3_df: pd.DataFrame,
    yearend_df: pd.DataFrame,
    quality_df: pd.DataFrame,
    chart_paths: list,
) -> str:

    today = date.today().strftime("%d.%m.%Y")

    # ── Pre-compute all table HTML strings ──────────────────────
    tbl_summary = _table_html(
        summary_df[["firma", "net_satis_toplam", "komisyon_toplam",
                     "satis_odulu_toplam", "katki_kari_toplam",
                     "katki_marji", "efektif_odeme_orani", "roi"]].rename(columns={
            "firma": "Firma", "net_satis_toplam": "Net Satış",
            "komisyon_toplam": "Komisyon", "satis_odulu_toplam": "Satış Ödülü",
            "katki_kari_toplam": "Katkı Kârı", "katki_marji": "Katkı Marjı",
            "efektif_odeme_orani": "Eff. Ödeme Oranı", "roi": "ROI",
        }),
        {
            "Net Satış": "tl", "Komisyon": "tl", "Satış Ödülü": "tl",
            "Katkı Kârı": "tl", "Katkı Marjı": "pct",
            "Eff. Ödeme Oranı": "pct", "ROI": "x",
        },
    )

    tbl_be = _table_html(
        be_df.rename(columns={
            "firma": "Firma", "sabit_maliyet": "Sabit Maliyet",
            "katki_marji_oran": "Katkı Marjı", "breakeven_net_satis": "Break-even Satış",
            "gercek_net_satis": "Gerçek Satış", "breakeven_asim": "BE Aşım",
            "guvenlik_marji": "Güvenlik Marjı",
        }),
        {
            "Sabit Maliyet": "tl", "Katkı Marjı": "pct",
            "Break-even Satış": "tl", "Gerçek Satış": "tl",
            "BE Aşım": "bool", "Güvenlik Marjı": "pct",
        },
    )

    tbl_roi = _table_html(
        roi_df.rename(columns={
            "firma": "Firma", "kanal_odemesi": "Kanal Ödemesi",
            "katki_kari_toplam": "Katkı Kârı", "roi": "ROI", "roi_formatted": "ROI (fmt)",
        }),
        {"Kanal Ödemesi": "tl", "Katkı Kârı": "tl", "ROI": "x"},
    )

    tbl_q3 = _table_html(
        q3_df.rename(columns={
            "firma": "Firma", "senaryo": "Senaryo",
            "net_satis_q3": "Net Satış Q3", "katki_kari_q3": "Katkı Kârı Q3",
            "komisyon_q3": "Komisyon Q3", "satis_odulu_q3": "Satış Ödülü Q3",
            "katki_marji_q3": "Katkı Marjı Q3",
        }),
        {
            "Net Satış Q3": "tl", "Katkı Kârı Q3": "tl",
            "Komisyon Q3": "tl", "Satış Ödülü Q3": "tl", "Katkı Marjı Q3": "pct",
        },
    )

    tbl_ye = _table_html(
        yearend_df.rename(columns={
            "firma": "Firma", "senaryo": "Senaryo",
            "net_satis_yil": "Net Satış Yıl", "katki_kari_yil": "Katkı Kârı Yıl",
            "komisyon_yil": "Komisyon Yıl", "satis_odulu_yil": "Satış Ödülü Yıl",
            "katki_marji_yil": "Katkı Marjı", "efektif_odeme": "Eff. Ödeme",
        }),
        {
            "Net Satış Yıl": "tl", "Katkı Kârı Yıl": "tl",
            "Komisyon Yıl": "tl", "Satış Ödülü Yıl": "tl",
            "Katkı Marjı": "pct", "Eff. Ödeme": "pct",
        },
    )

    tbl_quality = _table_html(
        quality_df.rename(columns={
            "firma": "Firma", "kalite_skoru": "Genel Skor",
            "skor_katki_marji": "Katkı Marjı Skoru", "skor_iade": "İade Skoru",
            "skor_yeni_musteri": "Yeni Müşteri Skoru", "skor_tahsilat": "Tahsilat Skoru",
        }),
    )

    # ── KPI values ──────────────────────────────────────────────
    total_net  = summary_df["net_satis_toplam"].sum()
    total_kom  = summary_df["komisyon_toplam"].sum()
    total_odul = summary_df["satis_odulu_toplam"].sum()
    total_kk   = summary_df["katki_kari_toplam"].sum()
    avg_km     = total_kk / total_net if total_net > 0 else 0
    best       = summary_df.nlargest(1, "katki_marji")["firma"].values[0]

    # ── Guardrail alerts ─────────────────────────────────────────
    from config.settings import MAX_REWARD_RATE, CONTRACT_COMMISSION_RATE
    threshold = MAX_REWARD_RATE + CONTRACT_COMMISSION_RATE

    alerts_html = ""
    for _, r in summary_df.iterrows():
        if r.get("guardrail_asim", False):
            alerts_html += (
                f'<div class="alert">'
                f'&#9888; <strong>{r["firma"]}</strong>: '
                f'Efektif ödeme oranı %{r["efektif_odeme_orani"]*100:.1f} → '
                f'Guardrail sınırı aşıldı!</div>'
            )
    if not alerts_html:
        alerts_html = '<div class="alert good">&#10003; Tüm firmalar guardrail sınırı içinde.</div>'

    # ── Image HTML ───────────────────────────────────────────────
    img_sales      = _img("01_aylik_net_satis", "Firma bazlı aylık net satış (Ay 1-5 gerçekleşen)")
    img_km         = _img("02_katki_marji", "Katkı Kârı (TL) ve Katkı Marjı (%)")
    img_epo        = _img("03_efektif_odeme_orani", "Efektif ödeme oranı — guardrail çizgisi")
    img_wf_a       = _img("04_waterfall_Firma_A", "Firma A Waterfall")
    img_wf_b       = _img("04_waterfall_Firma_B", "Firma B Waterfall")
    img_wf_c       = _img("04_waterfall_Firma_C", "Firma C Waterfall")
    img_wf_d       = _img("04_waterfall_Firma_D", "Firma D Waterfall")
    img_wf_e       = _img("04_waterfall_Firma_E", "Firma E Waterfall")
    img_wf_f       = _img("04_waterfall_Firma_F", "Firma F Waterfall")
    img_ye         = _img("05_yilsonu_senaryolar", "Yıl sonu net satış ve katkı kârı — 3 senaryo")
    img_q3         = _img("06_q3_senaryolar", "Q3 net satış ve katkı kârı — 3 senaryo")
    img_roi        = _img("07_roi_matrisi", "Katkı Kârı / Toplam Kanal Ödemesi")
    img_quality    = _img("08_musteri_kalitesi", "Bileşik müşteri kalitesi skoru (0-100)")
    img_trend      = _img("09_tahmin_trendi", "Ay 1-5 gerçekleşen + Ay 6-12 baz senaryo tahmini")

    guardrail_pct  = threshold * 100

    html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<title>Komisyon Kârlılık Raporu</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f9; color: #2c3e50; }}
  header {{ background: linear-gradient(135deg,#1a252f,#2980b9); color: white; padding: 30px 40px; }}
  header h1 {{ font-size: 2rem; margin-bottom: 6px; }}
  header p  {{ font-size: 0.95rem; opacity: .85; }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 30px 20px; }}
  section {{ background: white; border-radius: 12px; padding: 28px 32px; margin-bottom: 28px;
             box-shadow: 0 2px 12px rgba(0,0,0,.07); }}
  h2 {{ font-size: 1.3rem; color: #1a252f; margin-bottom: 18px;
        border-bottom: 3px solid #2980b9; padding-bottom: 8px; }}
  h3 {{ font-size: 1.05rem; color: #2c3e50; margin: 18px 0 10px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: .88rem; }}
  th {{ background: #2980b9; color: white; padding: 10px 12px; text-align: left; }}
  td {{ padding: 8px 12px; border-bottom: 1px solid #ecf0f1; }}
  tr:hover {{ background: #f8f9fa; }}
  .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit,minmax(200px,1fr)); gap:16px; margin-bottom:24px; }}
  .kpi {{ background:#f8f9fa; border-left:4px solid #2980b9; padding:16px 20px; border-radius:8px; }}
  .kpi .val {{ font-size:1.6rem; font-weight:700; color:#2980b9; }}
  .kpi .lbl {{ font-size:.82rem; color:#7f8c8d; margin-top:4px; }}
  .alert {{ background:#fef9e7; border-left:4px solid #f39c12; padding:12px 16px;
             margin:10px 0; border-radius:6px; font-size:.9rem; }}
  .good  {{ background:#eafaf1; border-left-color:#27ae60; }}
  figure {{ margin: 16px 0; text-align: center; }}
  figcaption {{ font-size:.82rem; color:#7f8c8d; margin-top:6px; }}
  .two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; }}
  footer {{ text-align:center; padding:20px; font-size:.8rem; color:#95a5a6; }}
</style>
</head>
<body>
<header>
  <h1>Komisyon &amp; Satış Ödülü Kârlılık Raporu</h1>
  <p>1 Yıllık Sözleşme | %10 Sabit Komisyon | 5 Farklı Ödül Skalası |
     Rapor: {today} | Ay 1-5 Gerçekleşen + Ay 6-12 Tahmin</p>
</header>
<div class="container">

  <section>
    <h2>&#128202; Özet Gösterge Tablosu (Ay 1-5 Gerçekleşen)</h2>
    <div class="kpi-grid">
      <div class="kpi"><div class="val">&#8378;{total_net/1_000_000:.1f}M</div><div class="lbl">Toplam Net Satış</div></div>
      <div class="kpi"><div class="val">&#8378;{total_kom/1_000:.0f}K</div><div class="lbl">Toplam Komisyon</div></div>
      <div class="kpi"><div class="val">&#8378;{total_odul/1_000:.0f}K</div><div class="lbl">Toplam Satış Ödülü</div></div>
      <div class="kpi"><div class="val">&#8378;{total_kk/1_000_000:.2f}M</div><div class="lbl">Toplam Katkı Kârı</div></div>
      <div class="kpi"><div class="val">{avg_km*100:.1f}%</div><div class="lbl">Ortalama Katkı Marjı</div></div>
      <div class="kpi"><div class="val">{best}</div><div class="lbl">&#127942; En Yüksek Katkı Marjı</div></div>
    </div>
    {alerts_html}
  </section>

  <section>
    <h2>&#128200; Aylık Net Satış Trendi</h2>
    {img_sales}
  </section>

  <section>
    <h2>&#128176; Firma Bazlı Katkı Kârı Analizi</h2>
    {img_km}
    <h3>Detay Tablo</h3>
    {tbl_summary}
  </section>

  <section>
    <h2>&#128678; Efektif Ödeme Oranı &amp; Guardrail Analizi</h2>
    {img_epo}
    <p style="margin-top:12px;font-size:.9rem;color:#555;">
      Guardrail = Brüt Marj %45 &minus; Değişken Ops %7 &minus; Komisyon %10 &minus; Hedef Kâr %15
      = <strong>%13 maks ödül + %10 komisyon = %{guardrail_pct:.0f} toplam</strong>
    </p>
  </section>

  <section>
    <h2>&#129695; Waterfall Kâr Analizi (Ay 1-5 Kümülatif)</h2>
    <div class="two-col">{img_wf_a}{img_wf_b}</div>
    <div class="two-col">{img_wf_c}{img_wf_d}</div>
    <div class="two-col">{img_wf_e}{img_wf_f}</div>
  </section>

  <section>
    <h2>&#128208; Kanal ROI Analizi</h2>
    {img_roi}
    {tbl_roi}
  </section>

  <section>
    <h2>&#9878;&#65039; Break-even Analizi</h2>
    {tbl_be}
  </section>

  <section>
    <h2>&#11088; Müşteri Kalitesi Skoru</h2>
    {img_quality}
    {tbl_quality}
  </section>

  <section>
    <h2>&#128302; Tahmin Trendi — Tam Yıl (Baz Senaryo)</h2>
    {img_trend}
  </section>

  <section>
    <h2>&#128197; 3. Çeyrek (Q3) Tahmin Senaryoları — Ay 7-9</h2>
    {img_q3}
    <h3>Q3 Detay Tablo</h3>
    {tbl_q3}
  </section>

  <section>
    <h2>&#127937; Yıl Sonu Tahmin Senaryoları (Kümülatif Ay 1-12)</h2>
    {img_ye}
    <h3>Yıl Sonu Detay Tablo</h3>
    {tbl_ye}
  </section>

  <section>
    <h2>&#128203; Metodoloji Notu</h2>
    <ul style="line-height:1.9;font-size:.92rem;padding-left:20px;">
      <li><strong>Komisyon:</strong> Net satış × %10 (sabit, sözleşmesel)</li>
      <li><strong>Ödül hesabı:</strong> Incremental (kademeli) — her dilimin oranı sadece o dilimdeki satışa uygulanır</li>
      <li><strong>Guardrail:</strong> Brüt Marj %45 − Değişken Ops %7 − Komisyon %10 − Hedef Kâr %15 = maks ödül %13</li>
      <li><strong>Katkı Kârı:</strong> Net Satış − Ürün Maliyeti − Komisyon − Satış Ödülü − Kanal Değişken Maliyeti</li>
      <li><strong>Tahmin:</strong> Lineer trend extrapolasyon + firma bazlı sezonsellik katsayıları</li>
      <li><strong>Senaryolar:</strong> Kötümser (satış ×0.85) | Baz (×1.00) | İyimser (satış ×1.15)</li>
      <li><strong>Müşteri Kalitesi:</strong> Katkı Marjı %40 + İade %25 + Yeni Müşteri %20 + Tahsilat %15</li>
    </ul>
  </section>

</div>
<footer>Komisyon Kârlılık Sistemi &mdash; {today} &mdash; Tüm veriler sentetiktir.</footer>
</body>
</html>"""

    out_path = OUTPUT / "rapor.html"
    out_path.write_text(html, encoding="utf-8")
    return str(out_path)
