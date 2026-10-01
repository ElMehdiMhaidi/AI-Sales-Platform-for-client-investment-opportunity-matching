from __future__ import annotations

import ast
import math
import re
from pathlib import Path
from typing import Iterable, List, Sequence, Set

import numpy as np
import pandas as pd


def parse_list(value) -> List[str]:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(x).strip() for x in value if str(x).strip()]
    s = str(value).strip()
    if not s:
        return []
    if s.startswith("[") and s.endswith("]"):
        try:
            out = ast.literal_eval(s)
            if isinstance(out, (list, tuple, set)):
                return [str(x).strip() for x in out if str(x).strip()]
        except Exception:
            pass
    return [p.strip() for p in re.split(r"\s*[;|]\s*", s) if p.strip()]


def norm_token(value: str) -> str:
    s = str(value).strip().lower().replace("&", "and")
    s = re.sub(r"[^a-z0-9+\-/ ]+", " ", s)
    s = re.sub(r"\s+", "_", s)
    return s.strip("_")


def norm_set(values: Iterable[str]) -> Set[str]:
    return {norm_token(v) for v in values if str(v).strip()}


def jaccard(a, b) -> float:
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def overlap_any(a, b) -> float:
    sa, sb = set(a), set(b)
    return 1.0 if sa and sb and sa & sb else 0.0


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    den = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / den) if den else 0.0


def recency_weight(days: float, half_life_days: float = 120.0) -> float:
    if days is None or pd.isna(days):
        return 0.0
    return float(math.exp(-math.log(2) * max(float(days), 0.0) / half_life_days))


def list_to_pipe(values: Iterable[str]) -> str:
    return "|".join(sorted({str(v).strip() for v in values if str(v).strip()}))


def pipe_to_set(value) -> Set[str]:
    return norm_set(parse_list(value))


def confidence_bucket(value) -> str:
    """Backwards-compatible converter to HIGH/MEDIUM/LOW.

    New market-event generation writes categories directly. Older seed files may
    still contain numeric confidence values.
    """
    s = str(value).strip().upper()
    if s in {"HIGH", "MEDIUM", "LOW"}:
        return s
    try:
        x = float(value)
        if x >= 0.90:
            return "HIGH"
        if x >= 0.70:
            return "MEDIUM"
        return "LOW"
    except Exception:
        return "LOW"
