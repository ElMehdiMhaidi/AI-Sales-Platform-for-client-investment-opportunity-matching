from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'outputs'; DATA=ROOT/'data'


def _parse_ids(v):
    if isinstance(v,list): return v
    try:
        x=ast.literal_eval(str(v)); return x if isinstance(x,list) else []
    except Exception: return []


def _run_command(args, label):
    with st.spinner(label):
        proc=subprocess.run(args,cwd=ROOT,text=True,capture_output=True)
    if proc.returncode!=0:
        st.error(proc.stderr.strip() or proc.stdout.strip() or f"Command failed: {' '.join(args)}")
        return False
    st.success(proc.stdout.strip().splitlines()[0] if proc.stdout.strip() else "Done")
    return True


def render():
    st.title("Who Should I Call?")
    st.caption("Select one or several market events. The engine ranks the most relevant eligible clients for each event.")

    # Upstream controls: market_events remains the exact same pipeline input.
    c1,c2=st.columns(2)
    with c1:
        if st.button("↻ Actualize latest infos about market",use_container_width=True,type="secondary"):
            if _run_command([sys.executable,str(ROOT/'market_event_generator'/'run_update.py')],"Refreshing market data + latest news…"):
                st.session_state['market_refreshed']=True
                st.rerun()
    with c2:
        if st.button("▶ Run the pipeline",use_container_width=True,type="primary"):
            if _run_command([sys.executable,str(ROOT/'run_pipeline.py')],"Running market-to-client ranking pipeline…"):
                st.session_state['market_refreshed']=False
                st.rerun()
    if st.session_state.get('market_refreshed'):
        st.info("Market events were refreshed. Click **Run the pipeline** to recompute client rankings.")

    ranking_path=OUT/'rankings.csv'
    if not ranking_path.exists():
        st.warning("No rankings yet. Click **Run the pipeline**."); return
    rankings=pd.read_csv(ranking_path); sources=pd.read_csv(DATA/'sources.csv') if (DATA/'sources.csv').exists() else pd.DataFrame()
    event_meta=rankings[['event_id','timestamp','asset_class','underlying','theme','strength','confidence','market_tone','source_ids','observation']].drop_duplicates('event_id').sort_values('event_id')
    labels={r.event_id:f"{r.event_id} · {r.underlying} · {r.theme}" for r in event_meta.itertuples(index=False)}
    ids=list(labels); selected=st.multiselect('Market events',ids,default=ids[:min(3,len(ids))],format_func=lambda x:labels[x]); top_n=st.slider('Clients per event',5,10,5)
    if not selected: st.info('Select at least one market event.'); return
    tabs=st.tabs([labels[e] for e in selected])
    for tab,eid in zip(tabs,selected):
        with tab:
            m=event_meta[event_meta.event_id==eid].iloc[0]
            a,b,c,d=st.columns(4); a.metric('Underlying',str(m.underlying)); b.metric('Strength',f"{float(m.strength):.2f}"); c.metric('Market confidence',str(m.confidence).upper()); d.metric('Market tone',str(m.market_tone).title())
            st.caption(str(m.observation))
            g=rankings[(rankings.event_id==eid)&(rankings.eligible==1)].sort_values('raw_score',ascending=False).head(top_n)
            if g.empty: st.warning('No eligible clients.'); continue
            for rank,(_,r) in enumerate(g.iterrows(),1):
                with st.expander(f"#{rank} {r.client_name} · {float(r.match_score):.0f}/100",expanded=rank<=2):
                    x,y,z=st.columns(3); x.metric('Match score',f"{float(r.match_score):.0f}/100"); y.metric('Selection confidence',f"{100*float(r.selection_confidence):.0f}%"); z.metric('Market confidence',str(r.confidence).upper())
                    st.markdown(f"**{r.client_type}** · {r.archetype}")
                    reasons=[r.get('reason_1',''),r.get('reason_2',''),r.get('reason_3','')]; reasons=[str(q) for q in reasons if pd.notna(q) and str(q).strip()]
                    if reasons:
                        st.markdown('**Why surfaced**'); st.markdown('  \n'.join([f"✓ {q}" for q in reasons]))
                    sids=_parse_ids(r.source_ids)
                    if sids:
                        st.markdown('**Supporting market evidence**')
                        for sid in sids[:5]:
                            row=sources[sources.source_id.astype(str)==str(sid)] if not sources.empty and 'source_id' in sources else pd.DataFrame()
                            if not row.empty:
                                sr=row.iloc[0]; label=f"{sid} · {sr.get('publisher','')} · {sr.get('published_at','')} · {sr.get('title','')} · {str(sr.get('source_confidence','LOW')).upper()}"
                                url=str(sr.get('url','') or '')
                                st.markdown(f"[{label}]({url})" if url.startswith('http') else label)
                            else: st.caption(str(sid))
