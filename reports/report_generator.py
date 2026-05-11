"""
HTML rapor üretici — Dark glassmorphism teması.
"""

import pandas as pd
from pathlib import Path
from datetime import date

OUTPUT = Path("output")

FIRM_COLORS = {
    "Firma_A": "#6366f1",
    "Firma_B": "#06b6d4",
    "Firma_C": "#10b981",
    "Firma_D": "#ef4444",
    "Firma_E": "#f59e0b",
    "Firma_F": "#8b5cf6",
}


def _fmt(val, kind="tl"):
    if not isinstance(val, (int, float)):
        return str(val)
    if kind == "tl":
        if abs(val) >= 1_000_000:
            return f"₺{val/1_000_000:.2f}M"
        return f"₺{val:,.0f}"
    if kind == "pct":
        return f"{val*100:.1f}%"
    if kind == "x":
        return f"{val:.2f}x"
    return str(val)


def _table_html(df: pd.DataFrame, col_formats: dict = None) -> str:
    col_formats = col_formats or {}
    rows = ""
    for i, (_, r) in enumerate(df.iterrows()):
        cells = ""
        for col in df.columns:
            fmt = col_formats.get(col, "")
            val = r[col]
            if fmt == "tl":
                cell = _fmt(val, "tl")
            elif fmt == "pct":
                cell = _fmt(val, "pct")
            elif fmt == "x":
                cell = _fmt(val, "x")
            elif fmt == "bool":
                cell = '<span class="badge-warn">⚠ Aşım</span>' if val else '<span class="badge-ok">✓ OK</span>'
            else:
                cell = str(val)
            # Firma adı sütununa renk dot ekle
            if col == "Firma" and str(val) in FIRM_COLORS:
                color = FIRM_COLORS[str(val)]
                cell = f'<span class="firm-dot" style="background:{color}"></span>{val}'
            cells += f"<td>{cell}</td>"
        cls = "row-alt" if i % 2 == 1 else ""
        rows += f'<tr class="{cls}">{cells}</tr>'

    headers = "".join(f"<th>{c}</th>" for c in df.columns)
    return f'<div class="table-wrap"><table><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table></div>'


def _img(name: str, caption: str = "") -> str:
    return (
        f'<figure class="chart-fig">'
        f'<img src="{name}.png" alt="{caption}" loading="lazy">'
        f'<figcaption>{caption}</figcaption></figure>'
    )


CSS = """
:root {
  --bg:       #0a0e1a;
  --bg2:      #0d1220;
  --surface:  #111827;
  --surface2: #1a2234;
  --border:   #1e2d45;
  --border2:  #243352;
  --text:     #f1f5f9;
  --text2:    #94a3b8;
  --text3:    #64748b;
  --accent:   #6366f1;
  --cyan:     #06b6d4;
  --emerald:  #10b981;
  --amber:    #f59e0b;
  --red:      #ef4444;
  --purple:   #8b5cf6;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html { scroll-behavior: smooth; }

body {
  font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  line-height: 1.6;
}

/* ── Top nav ── */
.topnav {
  position: sticky; top: 0; z-index: 100;
  background: rgba(10,14,26,.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 32px;
  padding: 0 40px; height: 56px;
}
.topnav .brand {
  font-size: 1rem; font-weight: 700; color: var(--text);
  letter-spacing: .02em; white-space: nowrap;
}
.topnav .brand span { color: var(--accent); }
.topnav a {
  font-size: .82rem; color: var(--text3); text-decoration: none;
  transition: color .2s;
}
.topnav a:hover { color: var(--accent); }

/* ── Hero ── */
header.hero {
  padding: 72px 40px 56px;
  background:
    radial-gradient(ellipse 70% 55% at 50% -10%, rgba(99,102,241,.18) 0%, transparent 70%),
    linear-gradient(180deg, #0d1525 0%, var(--bg) 100%);
  text-align: center;
  border-bottom: 1px solid var(--border);
}
header.hero h1 {
  font-size: 2.6rem; font-weight: 800; letter-spacing: -.03em;
  background: linear-gradient(135deg, #e0e7ff 0%, var(--accent) 50%, var(--cyan) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 14px;
}
header.hero .subtitle {
  color: var(--text2); font-size: .97rem;
  display: flex; gap: 16px; justify-content: center; flex-wrap: wrap;
}
header.hero .pill {
  background: rgba(99,102,241,.12); border: 1px solid rgba(99,102,241,.35);
  border-radius: 20px; padding: 4px 14px; font-size: .8rem; color: var(--accent);
}

/* ── Layout ── */
.container { max-width: 1280px; margin: 0 auto; padding: 40px 24px 80px; }

/* ── Section cards ── */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 28px;
  position: relative;
  overflow: hidden;
}
.card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(99,102,241,.5), transparent);
}

.card h2 {
  font-size: 1.15rem; font-weight: 700; color: var(--text);
  margin-bottom: 24px;
  display: flex; align-items: center; gap: 10px;
}
.card h2 .icon {
  width: 34px; height: 34px; border-radius: 10px;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 1rem;
  background: rgba(99,102,241,.15); border: 1px solid rgba(99,102,241,.3);
  flex-shrink: 0;
}
.card h3 { font-size: .97rem; font-weight: 600; color: var(--text2); margin: 22px 0 12px; }

/* ── KPI grid ── */
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 16px; margin-bottom: 28px; }

.kpi {
  background: var(--surface2);
  border: 1px solid var(--border2);
  border-radius: 14px;
  padding: 20px 22px;
  position: relative;
  overflow: hidden;
  transition: transform .2s, border-color .2s;
}
.kpi:hover { transform: translateY(-2px); border-color: rgba(99,102,241,.5); }
.kpi::after {
  content: '';
  position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, var(--accent), var(--cyan));
}

.kpi .val {
  font-size: 1.65rem; font-weight: 800; letter-spacing: -.03em;
  background: linear-gradient(135deg, var(--text) 0%, var(--accent) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}
.kpi .lbl { font-size: .78rem; color: var(--text3); margin-top: 5px; text-transform: uppercase; letter-spacing: .06em; }
.kpi .sub { font-size: .82rem; color: var(--text2); margin-top: 2px; }

/* Best firma kpi farklı */
.kpi.best .val {
  background: linear-gradient(135deg, var(--emerald), var(--cyan));
  -webkit-background-clip: text; background-clip: text;
}
.kpi.best::after { background: linear-gradient(90deg, var(--emerald), var(--cyan)); }

/* ── Alerts ── */
.alert {
  border-radius: 10px; padding: 12px 18px; margin: 10px 0;
  font-size: .88rem; display: flex; align-items: center; gap: 10px;
  border: 1px solid;
}
.alert.warn { background: rgba(245,158,11,.08); border-color: rgba(245,158,11,.3); color: var(--amber); }
.alert.good { background: rgba(16,185,129,.08); border-color: rgba(16,185,129,.3); color: var(--emerald); }
.alert.icon { font-size: 1.1rem; flex-shrink: 0; }

/* ── Tables ── */
.table-wrap { overflow-x: auto; border-radius: 12px; border: 1px solid var(--border); }
table { width: 100%; border-collapse: collapse; font-size: .84rem; }
thead tr { background: rgba(99,102,241,.12); }
th {
  padding: 12px 16px; text-align: left; font-weight: 600;
  font-size: .78rem; text-transform: uppercase; letter-spacing: .08em;
  color: var(--text2); white-space: nowrap; border-bottom: 1px solid var(--border);
}
td { padding: 10px 16px; color: var(--text); border-bottom: 1px solid var(--border); }
.row-alt td { background: rgba(255,255,255,.018); }
tr:last-child td { border-bottom: none; }
tr:hover td { background: rgba(99,102,241,.06); }

.firm-dot {
  display: inline-block; width: 8px; height: 8px; border-radius: 50%;
  margin-right: 8px; vertical-align: middle;
}

.badge-ok   { background: rgba(16,185,129,.15); color: var(--emerald);
               padding: 2px 10px; border-radius: 20px; font-size: .78rem; font-weight: 600; }
.badge-warn { background: rgba(245,158,11,.15); color: var(--amber);
               padding: 2px 10px; border-radius: 20px; font-size: .78rem; font-weight: 600; }

/* ── Charts ── */
.chart-fig { margin: 16px 0; text-align: center; }
.chart-fig img {
  max-width: 100%; border-radius: 12px;
  border: 1px solid var(--border);
}
.chart-fig figcaption { font-size: .78rem; color: var(--text3); margin-top: 8px; }

.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.three-col { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }

/* ── Firma legend pills ── */
.firm-pills { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; }
.firm-pill {
  display: flex; align-items: center; gap: 7px;
  background: var(--surface2); border: 1px solid var(--border2);
  border-radius: 20px; padding: 5px 14px; font-size: .8rem; color: var(--text2);
}
.firm-pill .dot { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }

/* ── Scenario legend ── */
.sc-legend { display: flex; gap: 20px; margin-bottom: 16px; }
.sc-item { display: flex; align-items: center; gap: 7px; font-size: .82rem; color: var(--text2); }
.sc-dot { width: 10px; height: 10px; border-radius: 3px; flex-shrink: 0; }

/* ── Methodology list ── */
.method-list { list-style: none; display: grid; gap: 12px; }
.method-list li {
  background: var(--surface2); border: 1px solid var(--border2);
  border-radius: 10px; padding: 14px 18px;
  display: flex; align-items: flex-start; gap: 12px;
  font-size: .88rem; color: var(--text2);
}
.method-list li .mico { font-size: 1.05rem; flex-shrink: 0; margin-top: 1px; }
.method-list li strong { color: var(--text); }

/* ── Decision banner ── */
.decision-banner {
  background: linear-gradient(135deg,
    rgba(99,102,241,.18) 0%,
    rgba(6,182,212,.12) 50%,
    rgba(16,185,129,.10) 100%);
  border: 1px solid rgba(99,102,241,.35);
  border-radius: 16px; padding: 28px 32px;
  margin-bottom: 28px;
  display: grid; grid-template-columns: 1fr 1fr; gap: 24px;
}
.decision-item h4 { font-size: .78rem; text-transform: uppercase;
  letter-spacing: .08em; color: var(--text3); margin-bottom: 6px; }
.decision-item .dval { font-size: 1.3rem; font-weight: 800; }
.decision-item .dsub { font-size: .85rem; color: var(--text2); margin-top: 4px; }

/* ── Footer ── */
footer {
  border-top: 1px solid var(--border);
  text-align: center; padding: 24px;
  font-size: .78rem; color: var(--text3);
}
footer span { color: var(--accent); }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ── Responsive ── */
@media (max-width: 900px) {
  header.hero h1 { font-size: 1.9rem; }
  .two-col, .three-col { grid-template-columns: 1fr; }
  .decision-banner { grid-template-columns: 1fr; }
  .topnav { gap: 14px; padding: 0 16px; }
}
"""


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

    today = date.today().strftime("%d %B %Y")

    # ── KPI değerleri ──────────────────────────────────────────
    total_net  = summary_df["net_satis_toplam"].sum()
    total_kom  = summary_df["komisyon_toplam"].sum()
    total_odul = summary_df["satis_odulu_toplam"].sum()
    total_kk   = summary_df["katki_kari_toplam"].sum()
    avg_km     = total_kk / total_net if total_net > 0 else 0
    best       = summary_df.nlargest(1, "katki_marji").iloc[0]
    worst      = summary_df.nsmallest(1, "katki_marji").iloc[0]

    # ── Guardrail ─────────────────────────────────────────────
    from config.settings import MAX_REWARD_RATE, CONTRACT_COMMISSION_RATE
    threshold  = (MAX_REWARD_RATE + CONTRACT_COMMISSION_RATE) * 100

    alerts_html = ""
    for _, r in summary_df.iterrows():
        if r.get("guardrail_asim", False):
            alerts_html += (
                f'<div class="alert warn"><span class="icon">⚠</span>'
                f'<strong>{r["firma"]}</strong>: Efektif ödeme oranı '
                f'%{r["efektif_odeme_orani"]*100:.1f} — Guardrail aşıldı!</div>'
            )
    if not alerts_html:
        alerts_html = (
            '<div class="alert good"><span class="icon">✓</span>'
            'Tüm firmalar guardrail sınırı içinde — kâr güvende.</div>'
        )

    # ── Firma pills ───────────────────────────────────────────
    firms_pill = "".join(
        f'<span class="firm-pill"><span class="dot" style="background:{FIRM_COLORS.get(f,"#6366f1")}"></span>{f}</span>'
        for f in summary_df["firma"]
    )

    # ── Senaryo legend ────────────────────────────────────────
    sc_legend = """
    <div class="sc-legend">
      <span class="sc-item"><span class="sc-dot" style="background:#ef4444"></span>Kötümser (×0.85)</span>
      <span class="sc-item"><span class="sc-dot" style="background:#6366f1"></span>Baz (×1.00)</span>
      <span class="sc-item"><span class="sc-dot" style="background:#10b981"></span>İyimser (×1.15)</span>
    </div>"""

    # ── Table HTML ────────────────────────────────────────────
    tbl_summary = _table_html(
        summary_df[["firma", "net_satis_toplam", "komisyon_toplam",
                     "satis_odulu_toplam", "katki_kari_toplam",
                     "katki_marji", "efektif_odeme_orani", "roi"]].rename(columns={
            "firma": "Firma", "net_satis_toplam": "Net Satış",
            "komisyon_toplam": "Komisyon", "satis_odulu_toplam": "Satış Ödülü",
            "katki_kari_toplam": "Katkı Kârı", "katki_marji": "Katkı Marjı",
            "efektif_odeme_orani": "Eff. Ödeme", "roi": "ROI",
        }),
        {"Net Satış": "tl", "Komisyon": "tl", "Satış Ödülü": "tl",
         "Katkı Kârı": "tl", "Katkı Marjı": "pct", "Eff. Ödeme": "pct", "ROI": "x"},
    )
    tbl_be = _table_html(
        be_df.rename(columns={
            "firma": "Firma", "sabit_maliyet": "Sabit Maliyet",
            "katki_marji_oran": "Katkı Marjı", "breakeven_net_satis": "BE Satış",
            "gercek_net_satis": "Gerçek Satış", "breakeven_asim": "BE Aşım",
            "guvenlik_marji": "Güvenlik Marjı",
        }),
        {"Sabit Maliyet": "tl", "Katkı Marjı": "pct", "BE Satış": "tl",
         "Gerçek Satış": "tl", "BE Aşım": "bool", "Güvenlik Marjı": "pct"},
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
            "katki_marji_q3": "Katkı Marjı",
        }),
        {"Net Satış Q3": "tl", "Katkı Kârı Q3": "tl",
         "Komisyon Q3": "tl", "Satış Ödülü Q3": "tl", "Katkı Marjı": "pct"},
    )
    tbl_ye = _table_html(
        yearend_df.rename(columns={
            "firma": "Firma", "senaryo": "Senaryo",
            "net_satis_yil": "Net Satış Yıl", "katki_kari_yil": "Katkı Kârı Yıl",
            "komisyon_yil": "Komisyon Yıl", "satis_odulu_yil": "Satış Ödülü Yıl",
            "katki_marji_yil": "Katkı Marjı", "efektif_odeme": "Eff. Ödeme",
        }),
        {"Net Satış Yıl": "tl", "Katkı Kârı Yıl": "tl",
         "Komisyon Yıl": "tl", "Satış Ödülü Yıl": "tl",
         "Katkı Marjı": "pct", "Eff. Ödeme": "pct"},
    )
    tbl_quality = _table_html(
        quality_df.rename(columns={
            "firma": "Firma", "kalite_skoru": "Genel Skor",
            "skor_katki_marji": "Katkı Marjı Sk.", "skor_iade": "İade Sk.",
            "skor_yeni_musteri": "Yeni Müşteri Sk.", "skor_tahsilat": "Tahsilat Sk.",
        }),
    )

    # ── Images ────────────────────────────────────────────────
    img_sales   = _img("01_aylik_net_satis",       "Aylık net satış — Ay 1-5 gerçekleşen")
    img_km      = _img("02_katki_marji",            "Katkı Kârı & Marjı karşılaştırması")
    img_epo     = _img("03_efektif_odeme_orani",    "Efektif ödeme oranı guardrail analizi")
    img_wf_a    = _img("04_waterfall_Firma_A",      "Firma A waterfall")
    img_wf_b    = _img("04_waterfall_Firma_B",      "Firma B waterfall")
    img_wf_c    = _img("04_waterfall_Firma_C",      "Firma C waterfall")
    img_wf_d    = _img("04_waterfall_Firma_D",      "Firma D waterfall")
    img_wf_e    = _img("04_waterfall_Firma_E",      "Firma E waterfall")
    img_wf_f    = _img("04_waterfall_Firma_F",      "Firma F waterfall")
    img_ye      = _img("05_yilsonu_senaryolar",     "Yıl sonu senaryoları — Net Satış & Katkı Kârı")
    img_q3      = _img("06_q3_senaryolar",          "Q3 senaryoları — Net Satış & Katkı Kârı")
    img_roi     = _img("07_roi_matrisi",            "Kanal ROI matrisi")
    img_quality = _img("08_musteri_kalitesi",       "Müşteri kalitesi bileşik skoru")
    img_trend   = _img("09_tahmin_trendi",          "Firma bazlı trend + baz senaryo tahmini")

    best_color  = FIRM_COLORS.get(best["firma"], "#6366f1")
    worst_color = FIRM_COLORS.get(worst["firma"], "#ef4444")

    html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Komisyon Kârlılık Raporu</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

<!-- ─ Top Nav ─────────────────────────────────────────────── -->
<nav class="topnav">
  <div class="brand">Komisyon<span>.</span>AI</div>
  <a href="#ozet">Özet</a>
  <a href="#katki">Katkı Marjı</a>
  <a href="#waterfall">Waterfall</a>
  <a href="#roi">ROI</a>
  <a href="#tahmin">Tahmin</a>
  <a href="#q3">Q3</a>
  <a href="#yilsonu">Yıl Sonu</a>
  <a href="#metod">Metodoloji</a>
</nav>

<!-- ─ Hero ───────────────────────────────────────────────── -->
<header class="hero">
  <h1>Komisyon &amp; Satış Ödülü<br>Kârlılık Raporu</h1>
  <div class="subtitle">
    <span class="pill">1 Yıllık Sözleşme</span>
    <span class="pill">%10 Sabit Komisyon</span>
    <span class="pill">5 Ödül Skalası</span>
    <span class="pill">Ay 5 → Q3 &amp; Yıl Sonu Tahmini</span>
    <span class="pill">{today}</span>
  </div>
</header>

<div class="container">

<!-- ─ Karar Özeti Banner ──────────────────────────────────── -->
<div class="decision-banner">
  <div class="decision-item">
    <h4>🏆 En Karlı Firma</h4>
    <div class="dval" style="color:{best_color}">{best["firma"]}</div>
    <div class="dsub">Katkı Marjı {best["katki_marji"]*100:.1f}% &nbsp;·&nbsp; ROI {best.get("roi",0):.2f}x</div>
  </div>
  <div class="decision-item">
    <h4>⚠ En Riskli Firma</h4>
    <div class="dval" style="color:{worst_color}">{worst["firma"]}</div>
    <div class="dsub">Katkı Marjı {worst["katki_marji"]*100:.1f}% &nbsp;·&nbsp; Yüksek iade/maliyet riski</div>
  </div>
  <div class="decision-item">
    <h4>📊 Toplam Katkı Kârı (Ay 1-5)</h4>
    <div class="dval" style="color:var(--emerald)">{_fmt(total_kk, "tl")}</div>
    <div class="dsub">Ort. katkı marjı {avg_km*100:.1f}%</div>
  </div>
  <div class="decision-item">
    <h4>💳 Toplam Kanal Ödemesi</h4>
    <div class="dval" style="color:var(--amber)">{_fmt(total_kom+total_odul, "tl")}</div>
    <div class="dsub">Komisyon {_fmt(total_kom,"tl")} + Ödül {_fmt(total_odul,"tl")}</div>
  </div>
</div>

<!-- ─ Özet KPI ───────────────────────────────────────────── -->
<section class="card" id="ozet">
  <h2><span class="icon">📈</span>Özet Gösterge Tablosu &nbsp;<small style="font-size:.75rem;font-weight:400;color:var(--text3)">Ay 1-5 Gerçekleşen</small></h2>
  <div class="firm-pills">{firms_pill}</div>
  <div class="kpi-grid">
    <div class="kpi">
      <div class="val">{_fmt(total_net,"tl")}</div>
      <div class="lbl">Toplam Net Satış</div>
    </div>
    <div class="kpi">
      <div class="val">{_fmt(total_kom,"tl")}</div>
      <div class="lbl">Toplam Komisyon (%10)</div>
    </div>
    <div class="kpi">
      <div class="val">{_fmt(total_odul,"tl")}</div>
      <div class="lbl">Toplam Satış Ödülü</div>
    </div>
    <div class="kpi best">
      <div class="val">{_fmt(total_kk,"tl")}</div>
      <div class="lbl">Toplam Katkı Kârı</div>
    </div>
    <div class="kpi">
      <div class="val">{avg_km*100:.1f}%</div>
      <div class="lbl">Ort. Katkı Marjı</div>
    </div>
    <div class="kpi">
      <div class="val">{threshold:.0f}%</div>
      <div class="lbl">Guardrail Sınırı</div>
      <div class="sub">Maks. toplam ödeme oranı</div>
    </div>
  </div>
  {alerts_html}
  {img_sales}
</section>

<!-- ─ Katkı Marjı ────────────────────────────────────────── -->
<section class="card" id="katki">
  <h2><span class="icon">💰</span>Katkı Kârı &amp; Marjı Analizi</h2>
  {img_km}
  {img_epo}
  <h3>Detay Tablo</h3>
  {tbl_summary}
</section>

<!-- ─ Waterfall ─────────────────────────────────────────── -->
<section class="card" id="waterfall">
  <h2><span class="icon">🪜</span>Waterfall Kâr Analizi &nbsp;<small style="font-size:.75rem;font-weight:400;color:var(--text3)">Ay 1-5 Kümülatif</small></h2>
  <div class="two-col">{img_wf_a}{img_wf_b}</div>
  <div class="two-col">{img_wf_c}{img_wf_d}</div>
  <div class="two-col">{img_wf_e}{img_wf_f}</div>
</section>

<!-- ─ ROI & Break-even ──────────────────────────────────── -->
<section class="card" id="roi">
  <h2><span class="icon">📐</span>ROI &amp; Break-even Analizi</h2>
  {img_roi}
  <h3>Kanal ROI Tablosu</h3>
  {tbl_roi}
  <h3>Break-even Analizi</h3>
  {tbl_be}
</section>

<!-- ─ Müşteri Kalitesi ───────────────────────────────────── -->
<section class="card">
  <h2><span class="icon">⭐</span>Müşteri Kalitesi Bileşik Skoru</h2>
  {img_quality}
  {tbl_quality}
</section>

<!-- ─ Tahmin Trend ───────────────────────────────────────── -->
<section class="card" id="tahmin">
  <h2><span class="icon">🔮</span>Tahmin Trendi &nbsp;<small style="font-size:.75rem;font-weight:400;color:var(--text3)">Baz Senaryo · Ay 1-12</small></h2>
  {img_trend}
</section>

<!-- ─ Q3 ────────────────────────────────────────────────── -->
<section class="card" id="q3">
  <h2><span class="icon">📅</span>3. Çeyrek (Q3) Tahmin &nbsp;<small style="font-size:.75rem;font-weight:400;color:var(--text3)">Ay 7-9</small></h2>
  {sc_legend}
  {img_q3}
  <h3>Q3 Detay Tablo</h3>
  {tbl_q3}
</section>

<!-- ─ Yıl Sonu ──────────────────────────────────────────── -->
<section class="card" id="yilsonu">
  <h2><span class="icon">🏁</span>Yıl Sonu Tahmin &nbsp;<small style="font-size:.75rem;font-weight:400;color:var(--text3)">Kümülatif Ay 1-12</small></h2>
  {sc_legend}
  {img_ye}
  <h3>Yıl Sonu Detay Tablo</h3>
  {tbl_ye}
</section>

<!-- ─ Metodoloji ─────────────────────────────────────────── -->
<section class="card" id="metod">
  <h2><span class="icon">📋</span>Metodoloji</h2>
  <ul class="method-list">
    <li><span class="mico">💳</span><div><strong>Komisyon:</strong> Net satış × %10 — sabit, sözleşmesel, tüm firmalar için aynı</div></li>
    <li><span class="mico">📊</span><div><strong>Ödül Hesabı:</strong> Incremental (kademeli) model — her dilimin oranı yalnızca o dilimdeki satışa uygulanır; cliff modeline kıyasla kârlılık daha kontrollüdür</div></li>
    <li><span class="mico">🚦</span><div><strong>Guardrail:</strong> Brüt Marj %45 − Değişken Ops %7 − Komisyon %10 − Hedef Kâr %15 = <strong>maks ödül %13 → toplam %{threshold:.0f}</strong></div></li>
    <li><span class="mico">💡</span><div><strong>Katkı Kârı:</strong> Net Satış − Ürün Maliyeti − Komisyon − Satış Ödülü − Kanal Değişken Maliyeti</div></li>
    <li><span class="mico">🔮</span><div><strong>Tahmin Modeli:</strong> Lineer trend extrapolasyon + firma bazlı sezonsellik katsayıları (Ay 1-5 gerçekleşenden türetilmiş)</div></li>
    <li><span class="mico">🎲</span><div><strong>Senaryolar:</strong> Kötümser (satış ×0.85, iade ×1.30, maliyet ×1.10) · Baz (×1.00) · İyimser (satış ×1.15, iade ×0.80, maliyet ×0.95)</div></li>
    <li><span class="mico">⭐</span><div><strong>Müşteri Kalitesi:</strong> Katkı Marjı %40 + İade %25 + Yeni Müşteri %20 + Tahsilat %15 ağırlıklı bileşik skor</div></li>
  </ul>
</section>

</div>

<footer>
  Komisyon Kârlılık Sistemi &nbsp;·&nbsp; <span>{today}</span> &nbsp;·&nbsp; Tüm veriler sentetiktir
</footer>

</body>
</html>"""

    out_path = OUTPUT / "rapor.html"
    out_path.write_text(html, encoding="utf-8")
    return str(out_path)
