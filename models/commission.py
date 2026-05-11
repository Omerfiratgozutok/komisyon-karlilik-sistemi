"""
Komisyon ve satış ödülü hesaplama motoru.

İki model:
  - incremental: Her dilimin ödül oranı sadece o dilimdeki satışa uygulanır (önerilen).
  - cliff:       Hangi dilimdeyse, o oran tüm net satışa uygulanır (dikkatli kullanılmalı).
"""

from config.settings import REWARD_SCALES, CONTRACT_COMMISSION_RATE


def calc_incremental_reward(net_satis: float, skala_adi: str) -> float:
    """Kademeli ödül: her aralıktaki satışa ilgili oranı uygular."""
    dilimler = REWARD_SCALES[skala_adi]
    toplam_odul = 0.0
    kalan = net_satis

    for alt, ust, oran in dilimler:
        if kalan <= 0:
            break
        if ust is None:
            pay = kalan
        else:
            pay = min(kalan, ust - alt)
        pay = max(0, pay)
        toplam_odul += pay * oran
        kalan -= pay

    return toplam_odul


def calc_cliff_reward(net_satis: float, skala_adi: str) -> float:
    """Cliff ödül: hangi dilime giriyorsa, o dilimin oranı tüm satışa uygulanır."""
    dilimler = REWARD_SCALES[skala_adi]
    oran = 0.0
    for alt, ust, r in dilimler:
        if ust is None or net_satis <= ust:
            if net_satis >= alt:
                oran = r
                break
    return net_satis * oran


def calc_commission_summary(row: dict, model: str = "incremental") -> dict:
    """
    Tek satır için tam komisyon + kârlılık hesabı.

    row anahtarları: net_satis, urun_maliyeti, kanal_degisken_maliyeti, skala
    """
    net_satis = row["net_satis"]
    skala     = row["skala"]

    komisyon = net_satis * CONTRACT_COMMISSION_RATE

    if model == "incremental":
        satis_odulu = calc_incremental_reward(net_satis, skala)
    else:
        satis_odulu = calc_cliff_reward(net_satis, skala)

    urun_maliyeti  = row.get("urun_maliyeti", 0)
    kanal_maliyeti = row.get("kanal_degisken_maliyeti", 0)

    katki_kari = net_satis - urun_maliyeti - komisyon - satis_odulu - kanal_maliyeti
    katki_marji = katki_kari / net_satis if net_satis > 0 else 0

    efektif_odeme_orani = (komisyon + satis_odulu) / net_satis if net_satis > 0 else 0

    marginal_katki = (
        (1 - row.get("birim_degisken_maliyet_orani", 0.55) - row.get("kanal_degisken_maliyet_orani", 0.07))
        - CONTRACT_COMMISSION_RATE
        - _marginal_reward_rate(net_satis, skala)
    )

    return {
        "komisyon": round(komisyon, 2),
        "satis_odulu": round(satis_odulu, 2),
        "toplam_kanal_odemesi": round(komisyon + satis_odulu, 2),
        "katki_kari": round(katki_kari, 2),
        "katki_marji": round(katki_marji, 4),
        "efektif_odeme_orani": round(efektif_odeme_orani, 4),
        "marginal_katki_orani": round(marginal_katki, 4),
    }


def _marginal_reward_rate(net_satis: float, skala_adi: str) -> float:
    """Mevcut satış seviyesinde bir sonraki 1 TL için ödül oranı."""
    dilimler = REWARD_SCALES[skala_adi]
    for alt, ust, oran in dilimler:
        if ust is None or net_satis < ust:
            if net_satis >= alt:
                return oran
    return dilimler[-1][2]


def enrich_dataframe(df, model: str = "incremental"):
    """DataFrame'deki her satır için komisyon özetini hesaplar ve ekler."""
    import pandas as pd

    # Hesaplanacak sütunları önceden çıkar (çift kolon önleme)
    drop_cols = ["komisyon", "satis_odulu", "toplam_kanal_odemesi",
                 "katki_kari", "katki_marji", "efektif_odeme_orani", "marginal_katki_orani"]
    base_df = df.drop(columns=[c for c in drop_cols if c in df.columns]).reset_index(drop=True)

    results = []
    for _, row in df.iterrows():
        r = row.to_dict()
        # enrich için ek profil bilgisi ekle
        if "birim_degisken_maliyet_orani" not in r:
            from config.settings import FIRM_PROFILES
            profile = FIRM_PROFILES.get(r.get("firma", ""), {})
            r["birim_degisken_maliyet_orani"] = profile.get("birim_degisken_maliyet_orani", 0.55)
            r["kanal_degisken_maliyet_orani"] = profile.get("kanal_degisken_maliyet_orani", 0.07)
        summary = calc_commission_summary(r, model=model)
        results.append(summary)

    summary_df = pd.DataFrame(results)
    return pd.concat([base_df, summary_df], axis=1)
