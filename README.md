# Client Opportunity Matching — Who Should I Call? v2

This version keeps the matching architecture intact and adds one **upstream Market Event Generator**.

The key design rule is unchanged:

> `data/market_events.csv` remains the input of the Who Should I Call pipeline.

The new module merely **regenerates that same file automatically** from latest news + quantitative market data. Its schema remains exactly the same 16 columns.

## Architecture

```text
market_event_generator/

Latest news / RSS                    Yahoo Finance daily prices
        ↓                                      ↓
news ingestion + NLP               1D/5D move + rolling history
        ↓                                      ↓
source quality                z-score / realized vol / percentile
        └──────────────────────┬───────────────┘
                               ↓
                         Event builder
                               ↓
                    data/market_events.csv
                               ↓
                         run_pipeline.py
                               ↓
                  Who Should I Call? ranking
```

No extra column is added to `market_events.csv`.

## Market-event schema — frozen

```text
event_id
timestamp
asset_class
underlying
signal_type
direction
strength
theme
observation
quant_observations
catalysts
source_ids
confidence
sales_themes
market_snapshot_id
quant_signal_id
```

## Confidence — no fake percentages

Market/source confidence is categorical:

- `HIGH`: specialist financial press or official primary source;
- `MEDIUM`: reputable business/general news or commercial market site;
- `LOW`: other secondary source.

The Streamlit front displays `HIGH / MEDIUM / LOW`, not `96%` or `98%`.

## Quantitative event strength

The current event is based on the last five sessions, but the generator downloads roughly one year of daily history because a z-score requires a historical comparison distribution.

Depending on the asset type:

- **Equity / FX**: 1D & 5D returns, 5D-return z-score, 20D realized volatility, volatility z-score, 1Y percentile.
- **Commodity**: the same + ATR and volume z-score where available.
- **Rates**: 1D / 5D yield changes in bp, 5D-move z-score, yield-level z-score, percentile.
- **Volatility**: current level, 5D level change, level z-score, 5D-change z-score, percentile.

The `strength` field is derived from statistical exceptionality, not manually assigned.

## Streamlit workflow

At the very top of **Who Should I Call?** there are now two controls:

### 1. `↻ Actualize latest infos about market`

Runs:

```bash
python market_event_generator/run_update.py
```

It:

1. downloads current market data from Yahoo Finance;
2. calculates the quant signals;
3. retrieves latest market news through RSS/news search;
4. performs lightweight NLP for theme, catalysts and observation;
5. stores auditable source records in `data/sources.csv`;
6. archives the previous `market_events.csv`;
7. writes a new `data/market_events.csv` with the **same 16 columns**.

It does **not** rerun the client ranking automatically.

### 2. `▶ Run the pipeline`

Runs:

```bash
python run_pipeline.py
```

It consumes the refreshed `data/market_events.csv`, builds Event × Client features, applies eligibility filters and reranks the coverage book.

So the intended demo is simply:

```text
Actualize latest infos about market
             ↓
new market_events.csv
             ↓
Run the pipeline
             ↓
updated Top 5–10 clients / event
```

## Model Lab

The Model Lab now shows **Train vs Test** rather than test metrics alone:

```text
Metric        Train   Test   Train-Test gap
NDCG@5
Precision@5
Recall@5
NDCG@10
Precision@10
Recall@10
```

The split is made by **whole Market Events** so the test events are unseen by the ranker.

## Install

```bash
cd client_opportunity_matching_v2
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Initial ranking:

```bash
python run_pipeline.py
```

Launch Streamlit:

```bash
streamlit run app/app.py
```

Then use the two buttons in the front end.

## Manual market refresh

You can also refresh without Streamlit:

```bash
python market_event_generator/run_update.py --min-strength 1.5 --max-events 20
```

Internet access is required for the refresh step. If retrieval fails or no instrument crosses the threshold, the previous `data/market_events.csv` is kept intact.

## Auditability

`data/sources.csv` keeps:

```text
source_id
publisher
published_at
source_type
title
url
source_confidence
```

Every Market Event keeps only the relevant `source_ids`, so the existing client cards remain traceable to their supporting market evidence.

## Important data note

The bundled client catalogue and training labels are synthetic benchmark data. They demonstrate the ranking architecture; they are not observed client behaviour or real CRM outcomes.
