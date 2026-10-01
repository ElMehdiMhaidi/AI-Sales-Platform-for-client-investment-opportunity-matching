from __future__ import annotations

import math
from typing import Dict
import numpy as np
import pandas as pd


def _safe_z(current, hist: pd.Series) -> float:
    hist = pd.to_numeric(hist, errors="coerce").replace([np.inf,-np.inf],np.nan).dropna()
    if len(hist) < 20: return 0.0
    std = float(hist.std(ddof=1))
    if not std or np.isnan(std): return 0.0
    return float((current - hist.mean()) / std)


def _percentile(series: pd.Series, value: float) -> float:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if len(s)==0: return 0.5
    return float((s <= value).mean())


def _atr_pct(df: pd.DataFrame, n=14) -> float:
    if not all(c in df for c in ["High","Low","Close"]): return float("nan")
    prev = df.Close.shift(1)
    tr = pd.concat([(df.High-df.Low).abs(),(df.High-prev).abs(),(df.Low-prev).abs()],axis=1).max(axis=1)
    atr = tr.rolling(n).mean().iloc[-1]
    return float(100*atr/df.Close.iloc[-1]) if pd.notna(atr) and df.Close.iloc[-1] else float("nan")


def price_signal(df: pd.DataFrame, asset_class: str) -> Dict:
    close=df.Close.astype(float)
    r1=float(close.pct_change().iloc[-1])
    r5_series=close.pct_change(5)
    r5=float(r5_series.iloc[-1])
    z5=_safe_z(r5,r5_series.iloc[:-1])
    daily=close.pct_change()
    rv20=float(daily.tail(20).std(ddof=1)*math.sqrt(252)) if len(daily.dropna())>=20 else 0.0
    hist_rv=daily.rolling(20).std(ddof=1)*math.sqrt(252)
    vol_z=_safe_z(rv20,hist_rv.iloc[:-1]) if rv20 else 0.0
    pct=_percentile(close.iloc[:-1],float(close.iloc[-1]))
    drawdown=float(close.iloc[-1]/close.max()-1)
    volume_z=0.0
    if "Volume" in df and df.Volume.notna().sum()>30 and float(df.Volume.iloc[-1] or 0)>0:
        volume_z=_safe_z(float(df.Volume.iloc[-1]),df.Volume.iloc[:-1])
    atr=_atr_pct(df) if asset_class.lower()=="commodity" else float("nan")
    strength=max(abs(z5),abs(vol_z))
    # Extreme price percentile is supporting, but does not replace a statistical move.
    if pct >= .98 or pct <= .02: strength=max(strength,1.50)
    return {
        "return_1d_pct":round(100*r1,3),"return_5d_pct":round(100*r5,3),"zscore_5d":round(z5,3),
        "realized_vol_20d_pct":round(100*rv20,3),"vol_zscore":round(vol_z,3),"price_percentile_1y":round(pct,3),
        "drawdown_from_1y_high_pct":round(100*drawdown,3),"volume_zscore":round(volume_z,3),
        "atr14_pct":None if np.isnan(atr) else round(atr,3),"strength":round(float(strength),3),
        "direction":"UP" if r5>0 else "DOWN" if r5<0 else "FLAT",
    }


def yield_signal(df: pd.DataFrame) -> Dict:
    y=df.Close.astype(float)
    d1=float((y.iloc[-1]-y.iloc[-2])*100) if len(y)>=2 else 0.0
    d5_series=(y-y.shift(5))*100
    d5=float(d5_series.iloc[-1])
    z5=_safe_z(d5,d5_series.iloc[:-1])
    level_z=_safe_z(float(y.iloc[-1]),y.iloc[:-1])
    pct=_percentile(y.iloc[:-1],float(y.iloc[-1]))
    strength=max(abs(z5),abs(level_z))
    if pct>=.98 or pct<=.02: strength=max(strength,1.50)
    return {"yield_pct":round(float(y.iloc[-1]),3),"move_1d_bp":round(d1,2),"move_5d_bp":round(d5,2),
            "zscore_5d_bp_move":round(z5,3),"yield_level_zscore":round(level_z,3),"yield_percentile_1y":round(pct,3),
            "strength":round(float(strength),3),"direction":"UP" if d5>0 else "DOWN" if d5<0 else "FLAT"}


def volatility_signal(df: pd.DataFrame) -> Dict:
    level=df.Close.astype(float); ch5=level-level.shift(5); current=float(level.iloc[-1]); delta=float(ch5.iloc[-1])
    level_z=_safe_z(current,level.iloc[:-1]); change_z=_safe_z(delta,ch5.iloc[:-1]); pct=_percentile(level.iloc[:-1],current)
    strength=max(abs(level_z),abs(change_z))
    if pct>=.98: strength=max(strength,1.50)
    return {"level":round(current,3),"change_5d":round(delta,3),"level_zscore":round(level_z,3),"change_5d_zscore":round(change_z,3),
            "level_percentile_1y":round(pct,3),"strength":round(float(strength),3),"direction":"UP" if delta>0 else "DOWN" if delta<0 else "FLAT"}


def compute_signal(df: pd.DataFrame, kind: str, asset_class: str) -> Dict:
    if len(df)<35: raise ValueError("Need at least 35 daily observations for robust rolling statistics")
    if kind=="yield": return yield_signal(df)
    if kind=="volatility": return volatility_signal(df)
    return price_signal(df,asset_class)
