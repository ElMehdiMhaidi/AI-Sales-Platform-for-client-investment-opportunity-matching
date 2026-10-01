from __future__ import annotations

from typing import Dict, List

import pandas as pd

from .utils import confidence_bucket, list_to_pipe, norm_set, norm_token, parse_list

ASSET_ALIASES = {
    "equities": "equity", "equity": "equity", "rates": "rates", "rate": "rates",
    "fixed_income": "rates", "fx": "fx", "foreign_exchange": "fx",
    "commodity": "commodity", "commodities": "commodity", "volatility": "volatility",
    "credit": "credit",
}

UNDERLYING_META: Dict[str, Dict[str, List[str]]] = {
    "brent": {"regions":["global"],"currencies":["usd"],"sectors":["energy"],"exposure_tags":["oil","energy","commodity"]},
    "wti": {"regions":["global"],"currencies":["usd"],"sectors":["energy"],"exposure_tags":["oil","energy","commodity"]},
    "gold": {"regions":["global"],"currencies":["usd"],"sectors":["metals"],"exposure_tags":["gold","metals","commodity"]},
    "copper": {"regions":["global"],"currencies":["usd"],"sectors":["metals","industrials"],"exposure_tags":["copper","metals","commodity"]},
    "eurusd": {"regions":["europe","us"],"currencies":["eur","usd"],"sectors":["fx"],"exposure_tags":["eurusd","fx"]},
    "gbpusd": {"regions":["uk","us"],"currencies":["gbp","usd"],"sectors":["fx"],"exposure_tags":["gbpusd","fx"]},
    "usdjpy": {"regions":["us","japan"],"currencies":["usd","jpy"],"sectors":["fx"],"exposure_tags":["usdjpy","fx"]},
    "sp500": {"regions":["us"],"currencies":["usd"],"sectors":["equity"],"exposure_tags":["us_equity","sp500","equity"]},
    "nasdaq": {"regions":["us"],"currencies":["usd"],"sectors":["technology","equity"],"exposure_tags":["us_equity","technology","nasdaq","equity"]},
    "eurostoxx50": {"regions":["europe"],"currencies":["eur"],"sectors":["equity"],"exposure_tags":["europe_equity","eurostoxx50","equity"]},
    "stoxx600": {"regions":["europe"],"currencies":["eur","gbp"],"sectors":["equity"],"exposure_tags":["europe_equity","stoxx600","equity"]},
    "vix": {"regions":["us"],"currencies":["usd"],"sectors":["volatility","equity"],"exposure_tags":["us_equity","volatility","options"]},
    "us10y": {"regions":["us"],"currencies":["usd"],"sectors":["rates"],"exposure_tags":["usd_rates","duration","10y","rates"]},
    "us30y": {"regions":["us"],"currencies":["usd"],"sectors":["rates"],"exposure_tags":["usd_rates","duration","30y","rates"]},
}

NEGATIVE_WORDS = {"sell-off","selloff","downside","stress","spike","widen","widening","drop","fall","risk","disruption","concern","weakness"}
POSITIVE_WORDS = {"rally","recovery","support","improve","tighten","tightening","upside","gain","strength"}


def standardize_asset_class(x: str) -> str:
    t = norm_token(x)
    return ASSET_ALIASES.get(t, t)


def infer_market_tone(text: str, direction: str, signal_type: str) -> str:
    t = str(text).lower()
    neg = sum(w in t for w in NEGATIVE_WORDS)
    pos = sum(w in t for w in POSITIVE_WORDS)
    st = norm_token(signal_type)
    if any(k in st for k in ["sell_off","move_down","spike","shock_up"]): neg += 1
    if any(k in st for k in ["rally","breakout_up"]): pos += 1
    return "negative" if neg > pos else "positive" if pos > neg else "neutral"


def build_event_text(row: pd.Series) -> str:
    sales = ", ".join(parse_list(row.get("sales_themes")))
    catalysts = "; ".join(parse_list(row.get("catalysts")))
    return ". ".join([
        f"Asset class: {row.get('asset_class','')}", f"Underlying: {row.get('underlying','')}",
        f"Theme: {row.get('theme','')}", f"Sales themes: {sales}",
        f"Observation: {row.get('observation','')}", f"Quant context: {row.get('quant_observations','')}",
        f"Catalysts: {catalysts}",
    ])


def process_market_events(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], errors="coerce")
    out["asset_class_std"] = out["asset_class"].map(standardize_asset_class)
    out["underlying_std"] = out["underlying"].astype(str).map(norm_token)
    out["direction_std"] = out["direction"].astype(str).str.upper().map({"UP":1,"DOWN":-1,"FLAT":0}).fillna(0).astype(int)
    out["theme_std"] = out["theme"].astype(str).map(norm_token)
    out["signal_type_std"] = out["signal_type"].astype(str).map(norm_token)
    out["sales_theme_tags"] = out["sales_themes"].apply(lambda x: list_to_pipe(norm_set(parse_list(x))))
    out["confidence"] = out["confidence"].map(confidence_bucket)
    regions=[]; currencies=[]; sectors=[]; exposure=[]
    for _, r in out.iterrows():
        meta = UNDERLYING_META.get(r["underlying_std"], {})
        regions.append(list_to_pipe(meta.get("regions", [])))
        currencies.append(list_to_pipe(meta.get("currencies", [])))
        sectors.append(list_to_pipe(meta.get("sectors", [])))
        tags = set(meta.get("exposure_tags", [])); tags.add(r["asset_class_std"])
        exposure.append(list_to_pipe(tags))
    out["event_regions"] = regions
    out["event_currencies"] = currencies
    out["event_sectors"] = sectors
    out["event_exposure_tags"] = exposure
    out["event_text"] = out.apply(build_event_text, axis=1)
    out["market_tone"] = out.apply(lambda r: infer_market_tone(r["event_text"], r["direction"], r["signal_type"]), axis=1)
    out["strength"] = pd.to_numeric(out["strength"], errors="coerce").fillna(0.0)
    return out
