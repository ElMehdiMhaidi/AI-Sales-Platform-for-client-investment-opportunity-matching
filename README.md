## Business Workflow

The project follows a proactive **Global Markets Sales / Client Coverage** workflow:

```text
Live Market Data + Financial News
              ↓
     Cross-Asset Event Detection
              ↓
     Market Intelligence Layer
              ↓
 Client Profiles + Recent History
              ↓
   Mandate & Eligibility Screening
              ↓
      Event × Client Matching
              ↓
     ML Opportunity Ranking
              ↓
 Explainable "Who Should I Call?"
```

The platform converts each detected Market Event into a **ranked Top-5/10 client shortlist**, together with the key exposures, client needs and market evidence supporting the opportunity.

---

## What the Project Adds

Global Markets Sales teams already have access to large volumes of market information, research and client data.

The challenge is turning these inputs into **prioritized, client-specific commercial opportunities**.

The platform automates the first coverage-screening layer across:

- **30+ cross-asset market series**
- **60 synthetic institutional client profiles**
- **1,400+ benchmark Event × Client combinations**
- Equities, Rates, FX, Commodities and Volatility

It helps answer:

- Which clients are exposed to the current market move?
- Which clients recently expressed a related investment or hedging need?
- Is the opportunity compatible with the client's mandate and risk constraints?
- Which accounts should Sales review first?
- What market evidence supports the recommendation?

The objective is therefore not to predict client conversion, but to transform **Market Intelligence into explainable Client Coverage prioritisation**.

---

## Architecture

The platform is built around two connected modules.

### 1. Cross-Asset Market Event Generator

The first module monitors **30+ market series** and transforms statistically significant market moves into structured Market Events.

It combines:

- Live / recent market data from Yahoo Finance
- Financial news retrieval
- 1D / 5D market moves
- Z-scores and historical percentiles
- Realised volatility
- Yield moves for Rates
- ATR / volume signals for Commodities
- Source-quality classification
- NLP-based theme and catalyst extraction

Each refresh can surface up to **30 current Market Events**, covering areas such as:

- Broad Equity indices
- AI / Technology
- Semiconductors
- FX
- Commodities
- Volatility
- Government Rates

The output is a structured and auditable `market_events.csv` containing:

```text
Market Move
+ Statistical Strength
+ Market Theme
+ Catalysts
+ Sales Themes
+ Supporting Sources
```

This becomes the input of the Client Opportunity Matching workflow.

---

### 2. Client Coverage & Opportunity Matching

Each Market Event is matched against a coverage universe of **60 synthetic institutional profiles**.

The client layer combines:

- Asset-class activity
- Market exposures
- Regions and currencies
- Investment objectives
- Hedging needs
- Risk profile
- Recent client interactions
- Client archetype priors
- Explicit mandate restrictions

Before any ML scoring is performed, the system applies **hard eligibility rules** to remove incompatible Event × Client combinations.

Eligible pairs are then represented through interpretable matching features including:

- Asset-class relevance
- Exposure overlap
- Region / currency alignment
- Investment-objective alignment
- Hedging-need relevance
- Directional exposure
- Semantic similarity
- Recent-need similarity
- Client recency
- Risk headroom
- Archetype relevance

This separates **hard mandate compatibility** from **soft commercial relevance**.

---

## Opportunity Ranking

The final prioritisation is performed using **XGBoost Learning-to-Rank**.

Rather than predicting whether a client will trade, the model solves a more realistic Sales problem:

> **For this Market Event, which eligible clients should appear first in the coverage shortlist?**

Training observations are structured as **Event × Client pairs** and grouped by Market Event.

The model learns nonlinear relationships between:

```text
Market Event
×
Client Exposure
×
Recent Needs
×
Mandate Compatibility
×
Commercial Relevance
```

and produces a ranked **Top-5/10 Sales opportunity list**.

The resulting Match Score is a relative ranking measure, not a transaction probability.

---

## Models & Methods

The project deliberately combines **deterministic controls** with **Machine Learning**:

- **Cross-Asset Quantitative Signals** — Market Event detection
- **NLP / Semantic Representations** — market and client textual relevance
- **Hard Eligibility Rules** — mandate and risk screening
- **Feature Engineering** — Event × Client commercial relevance
- **XGBoost Learning-to-Rank** — client prioritisation
- **Bootstrap Rank Stability** — selection-confidence diagnostics
- **Explainable ML** — feature-level rationale for surfaced opportunities

Model evaluation is performed on **unseen Market Events**, rather than randomly splitting Event × Client rows.

The Model Lab reports:

- NDCG@5 / NDCG@10
- Precision@5 / Precision@10
- Recall@5 / Recall@10
- Train vs Test performance
- Generalisation gap
- Feature importance
- Pair-feature diagnostics

---

## Streamlit Application

The project is delivered through an interactive Streamlit application designed around the Sales workflow.

### Who Should I Call?

Sales users can select several live Market Events and review the **Top-5/10 ranked client opportunities** for each event.

Each client card displays:

- Match Score
- Selection Confidence
- Market Confidence
- Main matching rationale
- Supporting market evidence

The application also allows the user to:

```text
Refresh Market Intelligence
        ↓
Generate new Market Events
        ↓
Run Client Opportunity Matching
        ↓
Review updated Client Rankings
```

### Model Lab

A separate technical view provides:

- Train vs Test ranking metrics
- Feature importance
- Event × Client feature breakdown
- Archetype inspection
- Rank-stability diagnostics

This keeps the Sales interface simple while preserving model transparency and auditability.

---

## Data Transparency

The project deliberately separates public market information from synthetic client data.

- **Market prices** come from public market-data sources.
- **Financial news** comes from public sources and remains source-linked.
- **Client profiles and interaction history** are synthetic.
- **Client archetypes** represent generic institutional client types.
- **Ranking labels** are benchmark relevance annotations, not observed CRM outcomes.

The project therefore demonstrates a realistic **Global Markets Sales decision-support architecture** without claiming to predict actual client trading behaviour.

---

## Why This Project

The objective is not to build another market-prediction model.

The project focuses on a different Front Office problem:

```text
Market Intelligence
        ↓
Client Coverage
        ↓
Mandate Eligibility
        ↓
Opportunity Matching
        ↓
Sales Prioritisation
        ↓
Explainable Client Action
```

It demonstrates how **Cross-Asset Market Intelligence, Machine Learning and client-specific constraints** can be combined into a practical Global Markets Sales workflow.

The final decision remains with the Sales person; the platform is designed to make the initial coverage-screening process **faster, more systematic and more explainable**.
