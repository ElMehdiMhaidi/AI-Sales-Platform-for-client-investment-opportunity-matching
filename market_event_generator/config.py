from __future__ import annotations

from dataclasses import dataclass
from typing import List

MARKET_EVENT_COLUMNS = [
    "event_id","timestamp","asset_class","underlying","signal_type","direction","strength",
    "theme","observation","quant_observations","catalysts","source_ids","confidence",
    "sales_themes","market_snapshot_id","quant_signal_id",
]


@dataclass(frozen=True)
class Instrument:
    underlying: str
    ticker: str
    asset_class: str
    kind: str  # price | yield | volatility
    news_query: str
    scale: float = 1.0


UNIVERSE: List[Instrument] = [

    # =========================================================
    # BROAD EQUITY INDICES
    # =========================================================
    Instrument(
        "SP500",
        "^GSPC",
        "Equity",
        "price",
        "S&P 500 US stocks market"
    ),

    Instrument(
        "NASDAQ",
        "^IXIC",
        "Equity",
        "price",
        "Nasdaq technology stocks market"
    ),

    Instrument(
        "NASDAQ100",
        "^NDX",
        "Equity",
        "price",
        "Nasdaq 100 technology AI megacap stocks"
    ),

    Instrument(
        "DOWJONES",
        "^DJI",
        "Equity",
        "price",
        "Dow Jones US stocks market"
    ),

    Instrument(
        "RUSSELL2000",
        "^RUT",
        "Equity",
        "price",
        "Russell 2000 US small cap stocks market"
    ),

    Instrument(
        "EUROSTOXX50",
        "^STOXX50E",
        "Equity",
        "price",
        "Euro Stoxx 50 European stocks market"
    ),

    Instrument(
        "STOXX600",
        "^STOXX",
        "Equity",
        "price",
        "STOXX 600 European shares market"
    ),

    Instrument(
        "DAX",
        "^GDAXI",
        "Equity",
        "price",
        "DAX German stocks market Germany"
    ),

    Instrument(
        "FTSE100",
        "^FTSE",
        "Equity",
        "price",
        "FTSE 100 UK stocks market Britain"
    ),

    Instrument(
        "NIKKEI225",
        "^N225",
        "Equity",
        "price",
        "Nikkei 225 Japanese stocks market Japan"
    ),


    # =========================================================
    # AI / SEMICONDUCTORS / TECHNOLOGY
    # =========================================================

    # Semiconductor benchmark
    Instrument(
        "PHLX_SEMICONDUCTORS",
        "^SOX",
        "Equity",
        "price",
        "semiconductor stocks chips AI Nvidia TSMC Broadcom AMD"
    ),

    # Semiconductor ETF proxy
    Instrument(
        "SEMICONDUCTORS_SMH",
        "SMH",
        "Equity",
        "price",
        "semiconductors AI chips Nvidia TSMC Broadcom data centers"
    ),

    # Second semiconductor proxy
    Instrument(
        "SEMICONDUCTORS_SOXX",
        "SOXX",
        "Equity",
        "price",
        "semiconductor industry AI chips processors GPU stocks"
    ),

    # Broad AI thematic exposure
    Instrument(
        "AI_TECH",
        "AIQ",
        "Equity",
        "price",
        "artificial intelligence AI technology big data stocks"
    ),

    # AI + robotics
    Instrument(
        "ROBOTICS_AI",
        "BOTZ",
        "Equity",
        "price",
        "artificial intelligence robotics automation AI stocks"
    ),

    # US technology sector
    Instrument(
        "US_TECH",
        "XLK",
        "Equity",
        "price",
        "US technology stocks AI Microsoft Nvidia Apple semiconductors"
    ),

    # Software
    Instrument(
        "SOFTWARE",
        "IGV",
        "Equity",
        "price",
        "software stocks AI enterprise software cloud technology"
    ),

    # Cloud computing
    Instrument(
        "CLOUD_COMPUTING",
        "SKYY",
        "Equity",
        "price",
        "cloud computing AI data centers hyperscalers technology"
    ),

    # Cybersecurity
    Instrument(
        "CYBERSECURITY",
        "CIBR",
        "Equity",
        "price",
        "cybersecurity stocks AI technology security software"
    ),


    # =========================================================
    # FX
    # =========================================================
    Instrument(
        "EURUSD",
        "EURUSD=X",
        "FX",
        "price",
        "EUR USD euro dollar foreign exchange ECB Federal Reserve"
    ),

    Instrument(
        "GBPUSD",
        "GBPUSD=X",
        "FX",
        "price",
        "GBP USD sterling dollar foreign exchange Bank of England"
    ),

    Instrument(
        "USDJPY",
        "JPY=X",
        "FX",
        "price",
        "USD JPY yen dollar foreign exchange Bank of Japan"
    ),


    # =========================================================
    # COMMODITIES
    # =========================================================
    Instrument(
        "BRENT",
        "BZ=F",
        "Commodity",
        "price",
        "Brent crude oil OPEC supply geopolitics energy market"
    ),

    Instrument(
        "WTI",
        "CL=F",
        "Commodity",
        "price",
        "WTI crude oil US supply inventories OPEC energy market"
    ),

    Instrument(
        "GOLD",
        "GC=F",
        "Commodity",
        "price",
        "gold price dollar yields Federal Reserve safe haven"
    ),

    Instrument(
        "COPPER",
        "HG=F",
        "Commodity",
        "price",
        "copper price China demand supply electrification AI data centers"
    ),


    # =========================================================
    # VOLATILITY
    # =========================================================
    Instrument(
        "VIX",
        "^VIX",
        "Volatility",
        "volatility",
        "VIX volatility US stocks options market risk sentiment"
    ),


    # =========================================================
    # RATES
    # =========================================================
    # Yahoo's Treasury yield indices are quoted approximately
    # 10x the yield percentage.

    Instrument(
        "US10Y",
        "^TNX",
        "Rates",
        "yield",
        "US 10-year Treasury yield Federal Reserve inflation rates",
        scale=0.1
    ),

    Instrument(
        "US30Y",
        "^TYX",
        "Rates",
        "yield",
        "US 30-year Treasury yield Federal Reserve inflation rates",
        scale=0.1
    ),
]


# =============================================================
# MARKET EVENT GENERATOR PARAMETERS
# =============================================================

MIN_STRENGTH = 1.0

# Historical window used to estimate z-scores / vol / percentiles
PRICE_HISTORY_PERIOD = "1y"

# News search lookback
NEWS_LOOKBACK_DAYS = 10

# Maximum number of articles retrieved for each instrument
MAX_NEWS_PER_INSTRUMENT = 8

# Expanded because the universe is now much larger
MAX_EVENTS = 30