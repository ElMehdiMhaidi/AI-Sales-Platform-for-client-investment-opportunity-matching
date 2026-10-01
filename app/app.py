from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(Path(__file__).parent))
from who_should_i_call import render as front
from model_lab import render as lab
from methodology import render as meth
st.set_page_config(page_title='Client Opportunity Matching',page_icon='📈',layout='wide')
with st.sidebar:
    st.title('Client Opportunity Matching'); page=st.radio('Section',['Who Should I Call?','Model Lab','Methodology']); st.divider(); st.caption('Human-in-the-loop Sales coverage decision support.')
{'Who Should I Call?':front,'Model Lab':lab,'Methodology':meth}[page]()
