import streamlit as st

def render():
    st.title('Methodology')
    st.subheader('0 · Market-event enrichment')
    st.code('Latest news / RSS + Yahoo Finance\n        ↓\nNLP + quantitative signal tests\n        ↓\nSame 16-column market_events.csv',language=None)
    st.write('The enrichment module is upstream only: it refreshes the existing market-events input without changing its schema.')
    st.subheader('1 · Market data')
    st.code('market_events.csv → cleaning / feature engineering / semantic representation → market features',language=None)
    st.subheader('2 · Client data')
    st.code('client catalogue + recent history + archetype priors → feature engineering → client features',language=None)
    st.subheader('3 · Matching engine')
    st.code('MARKET FEATURES     CLIENT FEATURES\n       │                  │\n       └───────┬──────────┘\n               ↓\n       Eligibility filters\n               ↓\n          Pair features\n               ↓\n       ML Learning-to-Rank\n               ↓\n          Match score\n               ↓\n             Top-N',language=None)
    st.latex(r'S_{semantic}(e,c)=\cos(\mathbf{E}_e,\mathbf{E}_c)')
    st.latex(r'Score(e,c)=f_{\theta}(X_{e,c})')
