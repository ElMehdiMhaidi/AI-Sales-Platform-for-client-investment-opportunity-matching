import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from market_event_generator.config import MARKET_EVENT_COLUMNS, Instrument
from market_event_generator.event_builder import build_event
from market_event_generator.quant_signals import compute_signal
from market_event_generator.source_quality import aggregate_confidence, classify_source


def sample_prices(n=260, shock=0.08):
    rng=np.random.default_rng(1); r=rng.normal(0,0.008,n); r[-5:]+=shock/5
    c=100*np.cumprod(1+r); return pd.DataFrame({'Open':c,'High':c*1.01,'Low':c*.99,'Close':c,'Volume':np.full(n,1_000_000)})


def test_price_signal_has_zscore_and_strength():
    s=compute_signal(sample_prices(),'price','Equity')
    assert 'zscore_5d' in s and 'realized_vol_20d_pct' in s
    assert s['strength'] >= 0


def test_event_schema_is_exactly_16_columns():
    inst=Instrument('SP500','^GSPC','Equity','price','S&P 500')
    sig=compute_signal(sample_prices(),'price','Equity')
    news=[{'source_id':'S1','publisher':'Reuters','published_at':'2026-10-01','source_type':'news','title':'Stocks move on rates','url':'https://reuters.com/x','source_confidence':'HIGH','text':'Rates repricing drove stocks.'}]
    src={'source_id':'YF_SP500','publisher':'Yahoo Finance','published_at':'','source_type':'market_data','title':'data','url':'','source_confidence':'MEDIUM','text':''}
    ev=build_event(inst,sig,news,src)
    assert list(ev.keys()) == MARKET_EVENT_COLUMNS


def test_confidence_is_categorical():
    assert classify_source('Reuters')=='HIGH'
    assert classify_source('Yahoo Finance')=='MEDIUM'
    assert aggregate_confidence(['LOW','HIGH'])=='HIGH'
