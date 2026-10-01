## Business Workflow

The project follows a realistic proactive Institutional Sales process:

```text
Live Market Data + Recent News
              ↓
      Market Event Detection
              ↓
 Commercial Market Interpretation
              ↓
 Client Profile + Recent History
              ↓
      Eligibility Screening
              ↓
   Event × Client Matching
              ↓
     Ranked Client Shortlist
              ↓
 Explainable "Who Should I Call?"
```

The result is a ranked list of clients for each market event, together with the main reasons why each opportunity was surfaced.

---

## What the Project Adds

Institutional Sales teams already have access to large amounts of market information and client data.

The real challenge is **connecting the two efficiently**.

This project automates the first screening layer by answering questions such as:

- Which clients are exposed to the current market move?
- Which clients recently expressed a related need?
- Which opportunities are compatible with the client's mandate and risk profile?
- Which clients should be reviewed first?
- What market evidence supports the opportunity?

The platform therefore converts **market information into client-specific commercial relevance**.

---

## Architecture

The system is split into two main modules.

### 1. Market Event Generator

The first module monitors a configurable cross-asset universe and generates structured Market Events.

It combines:

- Yahoo Finance market data
- Recent financial news
- Return and yield statistics
- Z-scores
- Realised volatility
- Price percentiles
- Source-quality classification
- Lightweight NLP for themes and catalysts

The output is a structured `market_events.csv` containing the event, its statistical strength, market narrative, catalysts, and supporting sources.

### 2. Client Opportunity Matching

The second module compares each Market Event with the institutional coverage book.

Client information includes:

- Asset classes
- Exposures
- Regions and currencies
- Investment objectives
- Hedging needs
- Risk profile
- Recent client history
- Client archetypes
- Explicit restrictions

Hard eligibility rules are applied first. Only eligible **Event × Client** pairs are then ranked.

The matching engine builds interpretable pair features such as:

- Asset-class match
- Exposure relevance
- Region and currency match
- Commercial-need alignment
- Directional relevance
- Semantic similarity
- Recent-need similarity
- Recency
- Risk headroom
- Archetype relevance

The final ranking is produced using **XGBoost Learning-to-Rank**, trained by Market Event groups.

---

## Models and Methods

The project uses a deliberately explainable stack:

- **Statistical market signals** for event detection
- **NLP and semantic representations** for textual relevance
- **Deterministic rules** for hard eligibility
- **XGBoost Learning-to-Rank** for client prioritisation
- **Bootstrap rank stability** for selection confidence

The model is evaluated using:

- NDCG@5 / NDCG@10
- Precision@5 / Precision@10
- Recall@5 / Recall@10

Train and test splits are performed by **whole Market Events**, ensuring that test events are unseen by the model.

---

## Streamlit Application

The Streamlit interface contains three views.

### Who Should I Call?

Select one or several Market Events and view the Top 5–10 ranked clients for each event.

Each client card shows:

- Match Score
- Selection Confidence
- Market Confidence
- Main matching reasons
- Supporting market evidence

### Model Lab

Used for model inspection and diagnostics:

- Train vs Test ranking metrics
- Feature importance
- Pair-feature breakdown
- Archetype explorer
- Rank-stability diagnostics

### Methodology

A compact explanation of the market-data pipeline, client-processing logic, and matching architecture.

---

## Data Transparency

The project deliberately separates real and synthetic data.

- **Market data and public news** come from public sources.
- **Client profiles and client history** are synthetic.
- **Ranking labels** are benchmark annotations and are not real CRM outcomes.

The project therefore demonstrates the ranking architecture and Institutional Sales workflow rather than claiming real client-conversion prediction.

---

## Why This Project

The core value of the project is not simply applying Machine Learning to financial data.

It demonstrates how market intelligence can be transformed into a practical **Institutional Sales coverage workflow**:

```text
Market Event
    ↓
Client Relevance
    ↓
Eligibility
    ↓
Prioritisation
    ↓
Explainable Sales Action
```

The objective is to help a Sales person focus attention faster while preserving **human judgement, traceability, and client constraints**.
