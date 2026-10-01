from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# Make project root importable when run as a script.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from market_event_generator.config import MARKET_EVENT_COLUMNS, MAX_EVENTS, MIN_STRENGTH, UNIVERSE
from market_event_generator.event_builder import build_event
from market_event_generator.market_data import download_universe
from market_event_generator.news_ingestion import fetch_google_news, yahoo_market_source
from market_event_generator.nlp import dedupe_news
from market_event_generator.quant_signals import compute_signal

DATA=ROOT/"data"; ARCHIVE=DATA/"archive"; ARCHIVE.mkdir(exist_ok=True)


def update_market_events(min_strength=MIN_STRENGTH,max_events=MAX_EVENTS):
    prices,price_errors=download_universe(UNIVERSE)
    events=[]; sources={}; diagnostics=[]
    for inst in UNIVERSE:
        if inst.underlying not in prices:
            diagnostics.append(f"SKIP {inst.underlying}: {price_errors.get(inst.underlying,'no market data')}")
            continue
        try:
            sig=compute_signal(prices[inst.underlying],inst.kind,inst.asset_class)
        except Exception as exc:
            diagnostics.append(f"SKIP {inst.underlying}: quant error {exc}")
            continue
        if float(sig.get("strength",0)) < min_strength:
            diagnostics.append(f"NO EVENT {inst.underlying}: strength={sig.get('strength')}")
            continue
        try:
            news=dedupe_news(fetch_google_news(inst.news_query))
        except Exception as exc:
            diagnostics.append(f"NEWS WARNING {inst.underlying}: {exc}"); news=[]
        yf_src=yahoo_market_source(inst.ticker,inst.underlying)
        for n in news+[yf_src]: sources[n["source_id"]]=n
        events.append(build_event(inst,sig,news,yf_src))
    events=sorted(events,key=lambda x:float(x["strength"]),reverse=True)[:max_events]
    if not events:
        raise RuntimeError("No event crossed the configured strength threshold. Existing market_events.csv was left untouched.")

    target=DATA/"market_events.csv"
    if target.exists():
        backup=ARCHIVE/f"market_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        shutil.copy2(target,backup)
    tmp=DATA/"market_events.tmp.csv"
    pd.DataFrame(events,columns=MARKET_EVENT_COLUMNS).to_csv(tmp,index=False)
    # Schema guard: absolutely no new columns.
    written=pd.read_csv(tmp)
    if list(written.columns)!=MARKET_EVENT_COLUMNS:
        raise RuntimeError("Schema guard failed: generated market_events.csv columns changed")
    tmp.replace(target)

    src_cols=["source_id","publisher","published_at","source_type","title","url","source_confidence"]
    pd.DataFrame([{k:v for k,v in s.items() if k in src_cols} for s in sources.values()],columns=src_cols).to_csv(DATA/"sources.csv",index=False)
    return {"events_written":len(events),"sources_written":len(sources),"diagnostics":diagnostics,"path":str(target)}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--min-strength",type=float,default=MIN_STRENGTH); ap.add_argument("--max-events",type=int,default=MAX_EVENTS)
    args=ap.parse_args(); result=update_market_events(args.min_strength,args.max_events)
    print(f"Updated {result['path']} with {result['events_written']} events and {result['sources_written']} source records.")
    for x in result["diagnostics"][-12:]: print(x)

if __name__=="__main__": main()
