import sys
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from src.market_features import process_market_events
from market_event_generator.config import MARKET_EVENT_COLUMNS

def test_seed_market_events_schema_unchanged():
    df=pd.read_csv(ROOT/'data'/'market_events.csv')
    assert list(df.columns)==MARKET_EVENT_COLUMNS

def test_confidence_backward_compatibility():
    df=pd.read_csv(ROOT/'data'/'market_events.csv').head(1).copy(); out=process_market_events(df)
    assert out.loc[out.index[0],'confidence'] in {'HIGH','MEDIUM','LOW'}
