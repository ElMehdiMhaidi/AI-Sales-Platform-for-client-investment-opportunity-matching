from __future__ import annotations

import numpy as np
import pandas as pd

from .utils import list_to_pipe, norm_set, norm_token, parse_list, recency_weight

LIST_COLS = [
    "asset_classes",
    "regions",
    "currencies",
    "objectives",
    "exposures",
    "hedging_needs",
    "allowed_asset_classes",
    "blocked_asset_classes",
    "blocked_regions",
    "blocked_currencies",
    "blocked_themes",
    "adverse_if_up",
    "adverse_if_down",
]

ARCHETYPE_LIST_COLS = [
    "typical_asset_classes",
    "typical_regions",
    "typical_currencies",
    "typical_exposures",
    "typical_needs",
    "typical_restrictions",
]


def _norm_pipe(v):
    return list_to_pipe(norm_set(parse_list(v)))


def _to_naive_datetime(value):
    """
    Convert any datetime/date/string to a timezone-naive pandas Timestamp.
    This avoids tz-aware vs tz-naive subtraction errors.
    """
    if value is None or pd.isna(value):
        return pd.NaT

    ts = pd.to_datetime(value, errors="coerce", utc=True)

    if pd.isna(ts):
        return pd.NaT

    return ts.tz_localize(None)


def process_clients(clients, history, archetypes, as_of=None):
    c = clients.copy()
    a = archetypes.copy()

    # -------------------------
    # Normalize list-like fields
    # -------------------------
    for col in LIST_COLS:
        if col not in c:
            c[col] = ""
        c[col] = c[col].apply(_norm_pipe)

    for col in ARCHETYPE_LIST_COLS:
        if col not in a:
            a[col] = ""
        a[col] = a[col].apply(_norm_pipe)

    # -------------------------
    # Merge client + archetype
    # -------------------------
    out = c.merge(
        a,
        on="archetype",
        how="left",
        suffixes=("", "_arch"),
    )

    # -------------------------
    # Effective risk limit
    # client-specific first,
    # archetype fallback second
    # -------------------------
    out["effective_max_event_strength"] = pd.to_numeric(
        out.get("max_event_strength"),
        errors="coerce",
    )

    out["effective_max_event_strength"] = (
        out["effective_max_event_strength"]
        .fillna(
            pd.to_numeric(
                out.get("archetype_max_event_strength"),
                errors="coerce",
            )
        )
        .fillna(3.0)
    )

    # -------------------------
    # Client history
    # -------------------------
    h = history.copy()

    h["date"] = pd.to_datetime(
        h["date"],
        errors="coerce",
        utc=True,
    ).dt.tz_localize(None)

    # Normalize as_of to timezone-naive as well
    if as_of is None:
        as_of = pd.Timestamp.today().normalize()
    else:
        as_of = _to_naive_datetime(as_of)

    # Extra safety
    if pd.isna(as_of):
        as_of = pd.Timestamp.today().normalize()

    h = h.sort_values(
        ["client_id", "date"],
        ascending=[True, False],
    )

    rows = []

    for cid, g in h.groupby("client_id", sort=False):
        g = g.head(3)
        latest = g.iloc[0]

        latest_date = latest["date"]

        if pd.notna(latest_date):
            days = max((as_of - latest_date).days, 0)
        else:
            days = np.nan

        recent_need_text = " | ".join(
            g["need_text"]
            .fillna("")
            .astype(str)
            .tolist()
        )

        rows.append(
            {
                "client_id": cid,
                "last_need_date": latest_date,
                "days_since_last_need": days,
                "recency_weight": recency_weight(days),
                "last_need_asset_class": norm_token(
                    latest.get("asset_class", "")
                ),
                "last_need_underlying": norm_token(
                    latest.get("underlying", "")
                ),
                "last_need_objective": norm_token(
                    latest.get("objective", "")
                ),
                "recent_need_text": recent_need_text,
            }
        )

    recent = pd.DataFrame(rows)

    if len(recent):
        out = out.merge(
            recent,
            on="client_id",
            how="left",
        )

    # -------------------------
    # Missing-value handling
    # -------------------------
    if "recency_weight" not in out:
        out["recency_weight"] = 0.0
    else:
        out["recency_weight"] = out["recency_weight"].fillna(0.0)

    if "recent_need_text" not in out:
        out["recent_need_text"] = ""
    else:
        out["recent_need_text"] = out["recent_need_text"].fillna("")

    if "days_since_last_need" not in out:
        out["days_since_last_need"] = np.nan

    # -------------------------
    # Semantic client text
    # -------------------------
    out["client_text"] = out.apply(
        lambda r: ". ".join(
            [
                f"Client type: {r.get('client_type', '')}",
                f"Archetype: {r.get('archetype', '')}",
                f"Asset classes: {r.get('asset_classes', '')}",
                f"Regions: {r.get('regions', '')}",
                f"Currencies: {r.get('currencies', '')}",
                f"Objectives: {r.get('objectives', '')}",
                f"Exposures: {r.get('exposures', '')}",
                f"Hedging needs: {r.get('hedging_needs', '')}",
                f"Recent need: {r.get('recent_need_text', '')}",
                f"Profile: {r.get('profile_text', '')}",
            ]
        ),
        axis=1,
    )

    return out