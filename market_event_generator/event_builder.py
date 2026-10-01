from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, List

from .config import MARKET_EVENT_COLUMNS, Instrument
from .nlp import build_theme, extract_catalysts, extractive_observation, sales_themes
from .source_quality import aggregate_confidence


def _signal_type(inst: Instrument, signal: Dict) -> str:
    d=signal.get("direction","FLAT")
    if inst.kind=="yield": return "RATE_SELL_OFF" if d=="UP" else "RATE_RALLY" if d=="DOWN" else "RATE_STABLE"
    if inst.kind=="volatility": return "VOLATILITY_SPIKE" if d=="UP" else "VOLATILITY_COMPRESSION" if d=="DOWN" else "VOLATILITY_STABLE"
    if inst.asset_class=="FX": return "FX_BREAKOUT_UP" if d=="UP" else "FX_BREAKOUT_DOWN" if d=="DOWN" else "FX_STABLE"
    if inst.asset_class=="Commodity": return "COMMODITY_SHOCK_UP" if d=="UP" else "COMMODITY_SHOCK_DOWN" if d=="DOWN" else "COMMODITY_STABLE"
    return "LARGE_PRICE_MOVE_UP" if d=="UP" else "LARGE_PRICE_MOVE_DOWN" if d=="DOWN" else "PRICE_STABLE"


def _fallback_observation(inst: Instrument, signal: Dict) -> str:
    if inst.kind=="yield": return f"{inst.underlying} moved {signal.get('move_5d_bp',0):+.1f} bp over five sessions."
    if inst.kind=="volatility": return f"{inst.underlying} changed {signal.get('change_5d',0):+.2f} points over five sessions."
    return f"{inst.underlying} moved {signal.get('return_5d_pct',0):+.2f}% over five sessions."


def build_event(inst: Instrument, signal: Dict, news: List[Dict], market_source: Dict) -> Dict:
    now=datetime.now(timezone.utc)
    stamp=now.strftime("%Y%m%d_%H%M")
    key=f"{stamp}_{inst.underlying}"
    short=hashlib.sha1(key.encode()).hexdigest()[:5].upper()
    source_rows=list(news)+[market_source]
    levels=[n.get("source_confidence","LOW") for n in news] or [market_source.get("source_confidence","MEDIUM")]
    event={
        "event_id":f"ME_{stamp}_{inst.underlying}_{short}",
        "timestamp":now.isoformat(timespec="seconds"),
        "asset_class":inst.asset_class,
        "underlying":inst.underlying,
        "signal_type":_signal_type(inst,signal),
        "direction":signal.get("direction","FLAT"),
        "strength":round(float(signal.get("strength",0)),3),
        "theme":build_theme(inst.asset_class,inst.underlying,signal),
        "observation":extractive_observation(news,_fallback_observation(inst,signal)),
        "quant_observations":repr({k:v for k,v in signal.items() if k not in {"strength","direction"}}),
        "catalysts":repr(extract_catalysts(news)),
        "source_ids":repr([x["source_id"] for x in source_rows]),
        "confidence":aggregate_confidence(levels),
        "sales_themes":repr(sales_themes(inst.asset_class,signal)),
        "market_snapshot_id":f"MS_{stamp}_{inst.underlying}",
        "quant_signal_id":f"QS_{stamp}_{inst.underlying}",
    }
    return event
