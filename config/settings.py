"""
Komisyon ve ödül sistemi yapılandırması.
1 yıllık sözleşme, sabit %10 komisyon + 5 farklı ödül skalası.
"""

# ─── Genel parametreler ────────────────────────────────────────────────────
CONTRACT_COMMISSION_RATE = 0.10        # Sabit kanal komisyonu
GROSS_MARGIN_RATE        = 0.45        # Brüt marj (ürün maliyeti sonrası)
VARIABLE_OPS_COST_RATE   = 0.07        # Lojistik + destek + ödeme altyapısı vb.
TARGET_NET_MARGIN        = 0.15        # Hedef minimum net kâr marjı

# Maksimum ödül bütçesi = brüt marj - değişken ops - komisyon - hedef kâr
MAX_REWARD_RATE = GROSS_MARGIN_RATE - VARIABLE_OPS_COST_RATE - CONTRACT_COMMISSION_RATE - TARGET_NET_MARGIN
# = 0.45 - 0.07 - 0.10 - 0.15 = 0.13  (%13)

CURRENT_MONTH = 5          # Şu an 5. aydayız
CONTRACT_MONTHS = 12       # 1 yıllık sözleşme

# ─── 5 Ödül Skalası (kademeli / incremental model) ────────────────────────
# Her skala: [(alt_limit, üst_limit, ödül_oranı), ...]
# Son dilim: üst_limit=None → sonsuz
REWARD_SCALES = {
    "Skala1": [                          # Düşük ciro / yeni firma
        (0,          500_000,   0.000),
        (500_000,  1_000_000,   0.020),
        (1_000_000, 2_000_000,  0.035),
        (2_000_000, None,       0.050),
    ],
    "Skala2": [                          # Orta ciro / standart
        (0,          500_000,   0.000),
        (500_000,  1_000_000,   0.025),
        (1_000_000, 2_000_000,  0.045),
        (2_000_000, 3_500_000,  0.060),
        (3_500_000, None,       0.075),
    ],
    "Skala3": [                          # Yüksek ciro / stratejik
        (0,          500_000,   0.000),
        (500_000,  1_500_000,   0.030),
        (1_500_000, 3_000_000,  0.055),
        (3_000_000, 5_000_000,  0.075),
        (5_000_000, None,       0.090),
    ],
    "Skala4": [                          # Premium / düşük iade
        (0,          750_000,   0.010),
        (750_000,  2_000_000,   0.035),
        (2_000_000, 4_000_000,  0.060),
        (4_000_000, None,       0.080),
    ],
    "Skala5": [                          # Agresif büyüme hedefi
        (0,          500_000,   0.005),
        (500_000,  1_500_000,   0.030),
        (1_500_000, 3_500_000,  0.060),
        (3_500_000, 6_000_000,  0.085),
        (6_000_000, None,       0.110),   # Bu skala %13 bütçe sınırına dikkat!
    ],
}

# ─── Firma profilleri ─────────────────────────────────────────────────────
FIRM_PROFILES = {
    "Firma_A": {
        "skala": "Skala3",
        "aylik_gross_satis_ortalama": 750_000,     # TL
        "gross_satis_std": 80_000,
        "iade_orani": 0.05,
        "iskonto_orani": 0.03,
        "birim_degisken_maliyet_orani": 0.55,      # Net satışın %55'i maliyet
        "kanal_degisken_maliyet_orani": 0.07,
        "tahsilat_gecikme_gun": 15,
        "yeni_musteri_orani": 0.20,
        "buyume_trendi": 0.04,                     # Aylık +%4 büyüme trendi
        "sezonsellik": [1.0, 0.95, 1.05, 1.10, 1.08, 1.15, 1.20, 1.18, 1.10, 1.05, 1.25, 1.40],
    },
    "Firma_B": {
        "skala": "Skala2",
        "aylik_gross_satis_ortalama": 520_000,
        "gross_satis_std": 50_000,
        "iade_orani": 0.02,
        "iskonto_orani": 0.02,
        "birim_degisken_maliyet_orani": 0.50,
        "kanal_degisken_maliyet_orani": 0.06,
        "tahsilat_gecikme_gun": 7,
        "yeni_musteri_orani": 0.35,
        "buyume_trendi": 0.06,
        "sezonsellik": [1.0, 1.0, 1.02, 1.05, 1.08, 1.10, 1.12, 1.15, 1.10, 1.05, 1.20, 1.30],
    },
    "Firma_C": {
        "skala": "Skala4",
        "aylik_gross_satis_ortalama": 420_000,
        "gross_satis_std": 30_000,
        "iade_orani": 0.01,
        "iskonto_orani": 0.01,
        "birim_degisken_maliyet_orani": 0.48,
        "kanal_degisken_maliyet_orani": 0.05,
        "tahsilat_gecikme_gun": 3,
        "yeni_musteri_orani": 0.50,
        "buyume_trendi": 0.08,
        "sezonsellik": [1.0, 1.02, 1.05, 1.08, 1.10, 1.12, 1.15, 1.18, 1.12, 1.08, 1.22, 1.35],
    },
    "Firma_D": {
        "skala": "Skala3",
        "aylik_gross_satis_ortalama": 900_000,
        "gross_satis_std": 120_000,
        "iade_orani": 0.12,
        "iskonto_orani": 0.06,
        "birim_degisken_maliyet_orani": 0.58,
        "kanal_degisken_maliyet_orani": 0.09,
        "tahsilat_gecikme_gun": 45,
        "yeni_musteri_orani": 0.10,
        "buyume_trendi": 0.02,
        "sezonsellik": [1.0, 0.98, 1.02, 1.05, 1.03, 1.08, 1.10, 1.07, 1.02, 0.98, 1.15, 1.25],
    },
    "Firma_E": {
        "skala": "Skala5",
        "aylik_gross_satis_ortalama": 610_000,
        "gross_satis_std": 90_000,
        "iade_orani": 0.04,
        "iskonto_orani": 0.03,
        "birim_degisken_maliyet_orani": 0.52,
        "kanal_degisken_maliyet_orani": 0.07,
        "tahsilat_gecikme_gun": 20,
        "yeni_musteri_orani": 0.40,
        "buyume_trendi": 0.10,
        "sezonsellik": [1.0, 0.98, 1.03, 1.08, 1.12, 1.18, 1.25, 1.22, 1.15, 1.10, 1.30, 1.45],
    },
    "Firma_F": {
        "skala": "Skala1",
        "aylik_gross_satis_ortalama": 280_000,
        "gross_satis_std": 60_000,
        "iade_orani": 0.15,
        "iskonto_orani": 0.08,
        "birim_degisken_maliyet_orani": 0.62,
        "kanal_degisken_maliyet_orani": 0.10,
        "tahsilat_gecikme_gun": 60,
        "yeni_musteri_orani": 0.05,
        "buyume_trendi": -0.01,
        "sezonsellik": [1.0, 0.92, 0.95, 1.00, 0.98, 1.02, 1.05, 1.02, 0.98, 0.95, 1.10, 1.20],
    },
}

# ─── Senaryo parametreleri ────────────────────────────────────────────────
SCENARIOS = {
    "kotu": {
        "satis_carpani": 0.85,
        "iade_carpani": 1.30,
        "maliyet_carpani": 1.10,
        "label": "Kötümser",
        "color": "#e74c3c",
    },
    "baz": {
        "satis_carpani": 1.00,
        "iade_carpani": 1.00,
        "maliyet_carpani": 1.00,
        "label": "Baz",
        "color": "#3498db",
    },
    "iyi": {
        "satis_carpani": 1.15,
        "iade_carpani": 0.80,
        "maliyet_carpani": 0.95,
        "label": "İyimser",
        "color": "#2ecc71",
    },
}
