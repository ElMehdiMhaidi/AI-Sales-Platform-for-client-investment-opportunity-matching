from __future__ import annotations

import ast
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.client_features import process_clients
from src.explainability import reasons_for_pair
from src.market_features import process_market_events
from src.pair_features import FEATURE_COLUMNS, build_pair_features
from src.ranker import bootstrap_selection_confidence, evaluate_ranking, fit_ranker, score_pairs, split_events
from src.semantic import SemanticEncoder

ROOT=Path(__file__).resolve().parent; DATA=ROOT/'data'; OUT=ROOT/'outputs'; MODELS=ROOT/'models'
OUT.mkdir(exist_ok=True); MODELS.mkdir(exist_ok=True)


def bootstrap_labels(pair_train: pd.DataFrame) -> pd.DataFrame:
    d=pair_train.copy()
    latent=(1.2*d.asset_match+2.2*d.exposure_match+2.5*d.commercial_need_match+1.4*d.recent_need_similarity+1.0*d.semantic_similarity+.8*d.directional_match+.4*d.region_match+.3*d.currency_match+.5*d.archetype_relevance+.3*d.risk_headroom)*d.eligible
    d['latent']=latent; rows=[]
    for ev,g in d.groupby('event_id'):
        elig=g[g.eligible==1].sort_values('latent',ascending=False); n=len(elig); n2=max(2,round(n*.16)) if n else 0; n1=max(3,round(n*.27)) if n else 0
        top2=set(elig.head(int(n2)).client_id); top1=set(elig.iloc[int(n2):int(n2+n1)].client_id)
        for _,r in g.iterrows(): rows.append({'event_id':ev,'client_id':r.client_id,'relevance_grade':2 if r.client_id in top2 else 1 if r.client_id in top1 else 0,'label_source':'synthetic_training_benchmark'})
    return pd.DataFrame(rows)


def main():
    live_raw=pd.read_csv(DATA/'market_events.csv'); train_raw=pd.read_csv(DATA/'training_events.csv'); clients_raw=pd.read_csv(DATA/'clients.csv'); hist=pd.read_csv(DATA/'client_history.csv'); arch=pd.read_csv(DATA/'archetypes.csv')
    live=process_market_events(live_raw); train=process_market_events(train_raw); as_of=pd.to_datetime(live.timestamp).max() if len(live) else pd.Timestamp.today()
    clients=process_clients(clients_raw,hist,arch,as_of=as_of)
    all_events=pd.concat([train,live],ignore_index=True)
    enc=SemanticEncoder(); corpus=all_events.event_text.fillna('').tolist()+clients.client_text.fillna('').tolist()+clients.recent_need_text.fillna('').tolist(); enc.fit(corpus); enc.save(MODELS/'semantic_encoder.joblib')
    ev_vec=enc.transform(all_events.event_text.fillna('').tolist()); cl_vec=enc.transform(clients.client_text.fillna('').tolist()); re_vec=enc.transform(clients.recent_need_text.fillna('').tolist())
    ev_emb={eid:ev_vec[i] for i,eid in enumerate(all_events.event_id)}; cl_emb={cid:cl_vec[i] for i,cid in enumerate(clients.client_id)}; re_emb={cid:re_vec[i] for i,cid in enumerate(clients.client_id)}
    ptrain=build_pair_features(train,clients,ev_emb,cl_emb,re_emb); plive=build_pair_features(live,clients,ev_emb,cl_emb,re_emb)
    labels_path=DATA/'labels.csv'
    if labels_path.exists(): labels=pd.read_csv(labels_path)
    else:
        labels=bootstrap_labels(ptrain); labels.to_csv(labels_path,index=False)
    ptrain=ptrain.merge(labels[['event_id','client_id','relevance_grade','label_source']],on=['event_id','client_id'],how='left'); ptrain.relevance_grade=ptrain.relevance_grade.fillna(0).astype(int); ptrain.label_source=ptrain.label_source.fillna('missing_label_zero')
    tr,te,tr_e,te_e=split_events(ptrain,.25,42); model=fit_ranker(tr); train_metrics=evaluate_ranking(model,tr); test_metrics=evaluate_ranking(model,te)
    import joblib; joblib.dump(model,MODELS/'xgb_ranker.joblib')
    scored=score_pairs(model,plive); conf=bootstrap_selection_confidence(tr,plive,top_n=5,n_boot=8); scored=scored.merge(conf,on=['event_id','client_id'],how='left')
    ccols=['client_id','client_name','client_type','archetype','risk_profile','recent_need_text']; ecols=['event_id','timestamp','asset_class','underlying','theme','strength','confidence','sales_themes','market_tone','source_ids','observation']
    scored=scored.merge(clients[ccols],on='client_id',how='left').merge(live[ecols],on='event_id',how='left')
    for i in range(1,4): scored[f'reason_{i}']=''
    for idx,r in scored.iterrows():
        for j,reason in enumerate(reasons_for_pair(r,3),1): scored.loc[idx,f'reason_{j}']=reason
    scored.sort_values(['event_id','eligible','raw_score'],ascending=[True,False,False]).to_csv(OUT/'rankings.csv',index=False)
    ptrain.to_csv(OUT/'training_pair_features.csv',index=False); plive.to_csv(OUT/'live_pair_features.csv',index=False); live.to_csv(OUT/'event_features.csv',index=False); clients.to_csv(OUT/'client_features.csv',index=False)
    pd.DataFrame({'feature':FEATURE_COLUMNS,'importance':model.feature_importances_}).sort_values('importance',ascending=False).to_csv(OUT/'feature_importance.csv',index=False)
    metrics={'train':{k:round(float(v),4) for k,v in train_metrics.items()},'test':{k:round(float(v),4) for k,v in test_metrics.items()},'n_labelled_pairs':len(ptrain),'n_train_events':len(tr_e),'n_test_events':len(te_e),'n_clients':clients.client_id.nunique(),'n_live_events':live.event_id.nunique(),'label_source_counts':labels.label_source.value_counts().to_dict()}
    metrics['gap']={k:round(metrics['train'][k]-metrics['test'][k],4) for k in metrics['train']}
    (OUT/'model_metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    print(json.dumps(metrics,indent=2)); print(f"Rankings written to {OUT/'rankings.csv'}")

if __name__=='__main__': main()
