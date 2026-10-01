from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import streamlit as st
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'outputs'; DATA=ROOT/'data'

def render():
    st.title('Model Lab'); st.caption('Training diagnostics, generalization and pair-feature transparency.')
    if not (OUT/'model_metrics.json').exists(): st.warning('Run the pipeline first.'); return
    m=json.loads((OUT/'model_metrics.json').read_text()); metrics=['ndcg@5','precision@5','recall@5','ndcg@10','precision@10','recall@10']
    st.subheader('Train vs Test performance')
    table=pd.DataFrame({'Metric':[x.upper() for x in metrics],'Train':[m['train'][x] for x in metrics],'Test':[m['test'][x] for x in metrics],'Train − Test gap':[m['gap'][x] for x in metrics]})
    st.dataframe(table,use_container_width=True,hide_index=True)
    st.caption(f"{m['n_labelled_pairs']} labelled pairs · {m['n_train_events']} train events · {m['n_test_events']} completely unseen test events · {m['n_clients']} clients")
    st.info('Test performance is the important out-of-sample result. Train metrics are displayed to diagnose overfitting; the gap should remain controlled.')
    imp=pd.read_csv(OUT/'feature_importance.csv'); st.subheader('Feature importance'); st.bar_chart(imp.head(12).set_index('feature')[['importance']])
    rankings=pd.read_csv(OUT/'rankings.csv'); pairs=pd.read_csv(OUT/'live_pair_features.csv')
    st.subheader('Pair feature breakdown')
    eid=st.selectbox('Market event',sorted(rankings.event_id.unique())); choices=rankings[(rankings.event_id==eid)&(rankings.eligible==1)].sort_values('raw_score',ascending=False); cmap=dict(zip(choices.client_id,choices.client_name))
    if cmap:
        cid=st.selectbox('Client',list(cmap),format_func=lambda x:cmap[x]); row=pairs[(pairs.event_id==eid)&(pairs.client_id==cid)].iloc[0]
        cols=['asset_match','exposure_match','region_match','currency_match','commercial_need_match','directional_match','semantic_similarity','recent_need_similarity','recency_weight','risk_headroom','archetype_relevance']
        st.dataframe(pd.DataFrame({'Feature':cols,'Value':[round(float(row[c]),4) for c in cols]}),use_container_width=True,hide_index=True)
    st.subheader('Archetype explorer'); arch=pd.read_csv(DATA/'archetypes.csv'); a=st.selectbox('Archetype',sorted(arch.archetype.unique())); st.dataframe(arch[arch.archetype==a].T,use_container_width=True)
