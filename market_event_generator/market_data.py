from __future__ import annotations

from typing import Dict
import pandas as pd
import yfinance as yf

from .config import Instrument, PRICE_HISTORY_PERIOD


def download_instrument(instrument: Instrument, period: str = PRICE_HISTORY_PERIOD) -> pd.DataFrame:
    df = yf.download(instrument.ticker, period=period, interval="1d", auto_adjust=True, progress=False, threads=False)
    if df is None or df.empty:
        raise RuntimeError(f"No Yahoo Finance data for {instrument.ticker}")
    # yfinance may return MultiIndex even for one symbol.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    needed = [c for c in ["Open","High","Low","Close","Volume"] if c in df.columns]
    df = df[needed].dropna(subset=["Close"]).copy()
    for c in ["Open","High","Low","Close"]:
        if c in df: df[c] = pd.to_numeric(df[c], errors="coerce") * instrument.scale
    if "Volume" in df: df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce")
    return df.dropna(subset=["Close"])


def download_universe(universe) -> Dict[str, pd.DataFrame]:
    out = {}
    errors = {}
    for inst in universe:
        try:
            out[inst.underlying] = download_instrument(inst)
        except Exception as exc:
            errors[inst.underlying] = str(exc)
    return out, errors
