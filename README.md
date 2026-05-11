# Komisyon & Satış Ödülü Kârlılık Sistemi

> 1 Yıllık Sözleşme | %10 Sabit Komisyon | 5 Farklı Ödül Skalası  
> 5. Ay Gerçekleşen + Q3 & Yıl Sonu Tahmin Senaryoları

---

## Proje Özeti

Bu sistem, 6 farklı firmayla yapılan 1 yıllık komisyon sözleşmelerinin karlılığını hesaplar, tahmin eder ve raporlar. Döküman metodolojisi: **Firma Komisyon ve Satış Ödülü Modelinde Kârlılık Hesaplama ve Karar Metodolojisi**.

### Temel Guardrail

```
Maks Ödül Bütçesi = Brüt Marj %45 − Değişken Ops %7 − Komisyon %10 − Hedef Kâr %15 = %13
```

---

## Proje Yapısı

```
komisyon-karlilik-sistemi/
├── config/
│   └── settings.py          # 5 ödül skalası, firma profilleri, senaryo parametreleri
├── data/
│   └── generator.py         # Sentetik veri üretici (trend + sezonsellik)
├── models/
│   ├── commission.py        # Komisyon motoru: cliff & incremental modeller
│   ├── profitability.py     # Katkı marjı, break-even, ROI, waterfall, cohort
│   └── forecasting.py      # Lineer trend + sezonsellik tabanlı Q3 & yıl sonu tahmini
├── analysis/
│   └── sensitivity.py       # Duyarlılık & tornado analizi
├── visualization/
│   └── charts.py            # 9 matplotlib grafiği
├── reports/
│   └── report_generator.py  # Tek sayfalık HTML rapor
├── output/                  # Üretilen grafikler + CSV + HTML (gitignore)
└── main.py                  # Tek komutla tüm pipeline
```

---

## Kurulum

```bash
git clone https://github.com/Omerfiratgozutok/komisyon-karlilik-sistemi.git
cd komisyon-karlilik-sistemi
pip install -r requirements.txt
python main.py
```

Rapor `output/rapor.html` dosyasında açılır.

---

## Analiz Modülleri

| Modül | Açıklama |
|---|---|
| **Komisyon Motoru** | Cliff ve Incremental modeller; 5 farklı skala |
| **Katkı Marjı** | Net Satış → Katkı Kârı P&L waterfall |
| **Break-even** | Firma bazlı başa baş satış ve güvenlik marjı |
| **ROI** | Katkı Kârı / Toplam Kanal Ödemesi |
| **Tahmin** | Ay 1-5 gerçekleşen → Ay 6-12 lineer trend + sezonsellik |
| **Q3 Senaryoları** | Ay 7-9: Kötümser / Baz / İyimser |
| **Yıl Sonu Senaryoları** | Kümülatif Ay 1-12: 3 senaryo |
| **Duyarlılık** | Satış ±%20, iade ±2pp, maliyet ±5pp |
| **Müşteri Kalitesi** | Katkı Marjı %40 + İade %25 + Yeni Müşteri %20 + Tahsilat %15 |

---

## 5 Ödül Skalası

| Skala | Hedef Kitle | Maks Ödül Oranı |
|---|---|---|
| Skala 1 | Yeni / düşük ciro firma | %5.0 |
| Skala 2 | Orta ciro / standart | %7.5 |
| Skala 3 | Yüksek ciro / stratejik | %9.0 |
| Skala 4 | Premium / düşük iade | %8.0 |
| Skala 5 | Agresif büyüme hedefi | %11.0 |

---

## Örnek Çıktılar (Baz Senaryo)

### Ay 1-5 Gerçekleşen

| Firma | Net Satış | Katkı Marjı | ROI |
|---|---|---|---|
| Firma_C | ₺2.5M | %36 | 3.27x |
| Firma_B | ₺2.8M | %34 | 3.37x |
| Firma_E | ₺4.0M | %30 | 2.72x |
| Firma_A | ₺4.1M | %27 | 2.44x |
| Firma_D | ₺3.7M | %22 | 2.00x |
| Firma_F | ₺1.2M | %18 | 1.80x |

### Yıl Sonu Tahmini (Baz Senaryo Kümülatif)

| Firma | Net Satış | Katkı Kârı | Katkı Marjı |
|---|---|---|---|
| Firma_E | ₺15.1M | ₺4.3M | %29 |
| Firma_A | ₺12.8M | ₺3.4M | %26 |
| Firma_C | ₺9.2M | ₺3.3M | %36 |
| Firma_B | ₺9.1M | ₺3.0M | %33 |
| Firma_D | ₺10.6M | ₺2.3M | %22 |
| Firma_F | ₺2.1M | ₺0.4M | %18 |

---

## Karar Kuralı

> Yüksek satış yapan firma **otomatik olarak** en değerli firma değildir.  
> En değerli firma: **yüksek net satış + düşük iade + yüksek katkı marjı + düşük operasyon maliyeti + iyi müşteri kalitesi** kombinasyonuna sahip firmadır.

---

## Geliştirme

- `config/settings.py` dosyasından gerçek firma profilleri ve skala parametreleri güncellenir
- `data/generator.py` yerini gerçek ERP/satış verisiyle değiştirilebilir
- Cliff model için `enrich_dataframe(df, model="cliff")` kullanılabilir
