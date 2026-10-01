# Market Event Generator

This folder is **upstream** of the existing Who Should I Call pipeline.

It does not change the schema of `data/market_events.csv`. It simply generates that same input more automatically:

```text
Latest news / RSS                    Yahoo Finance daily history
        ↓                                      ↓
news ingestion + NLP             current 1D/5D move + rolling stats
        ↓                                      ↓
source quality                  z-score / vol / percentile / ATR
        └────────────────────┬─────────────────┘
                             ↓
                       event builder
                             ↓
                 data/market_events.csv
                             ↓
                  existing matching pipeline
```

`market_events.csv` always keeps exactly these 16 columns:

`event_id, timestamp, asset_class, underlying, signal_type, direction, strength, theme, observation, quant_observations, catalysts, source_ids, confidence, sales_themes, market_snapshot_id, quant_signal_id`.

## Confidence

No fake percentages. `confidence` is categorical:

- **HIGH**: specialist financial press or primary official sources;
- **MEDIUM**: reputable business/general news or commercial market sites;
- **LOW**: other secondary sources.

## Strength

The current observation uses the last 5 sessions, but a longer daily history is downloaded because a z-score requires a comparison distribution. The generator uses asset-appropriate statistics:

- Equity / FX: 1D & 5D return, 5D-return z-score, 20D realized volatility, vol z-score, 1Y percentile.
- Commodities: same plus ATR and volume z-score when available.
- Rates: 1D/5D yield move in bp, z-score of 5D bp move, yield-level z-score and percentile.
- Volatility index: level z-score, 5D level-change z-score and percentile.

`strength` is the dominant statistical exceptionality measure (mainly absolute 5D-move / level-volatility z-scores), not an arbitrary editorial score.

## Run manually

```bash
python market_event_generator/run_update.py
```

The previous `market_events.csv` is archived under `data/archive/` before replacement. If data retrieval fails or no event crosses the threshold, the existing file is left untouched.
