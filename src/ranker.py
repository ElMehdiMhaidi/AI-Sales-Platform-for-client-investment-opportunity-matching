from __future__ import annotations
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import ndcg_score
from xgboost import XGBRanker
from .pair_features import FEATURE_COLUMNS


def split_events(df,test_size=0.25,random_state=42):
    rng=np.random.default_rng(random_state); ev=np.array(sorted(df.event_id.unique())); rng.shuffle(ev)
    n=max(1,int(round(len(ev)*test_size))); test=set(ev[:n])
    return df[~df.event_id.isin(test)].copy(),df[df.event_id.isin(test)].copy(),sorted(set(ev[n:])),sorted(test)

def fit_ranker(df,random_state=42,n_estimators=180):
    d=df[df.eligible==1].sort_values(["event_id","client_id"]).reset_index(drop=True)
    groups=d.groupby("event_id",sort=False).size().to_numpy()
    m=XGBRanker(objective="rank:ndcg",eval_metric="ndcg@5",tree_method="hist",n_estimators=n_estimators,max_depth=4,learning_rate=.04,subsample=.9,colsample_bytree=.9,random_state=random_state,lambdarank_pair_method="topk",lambdarank_num_pair_per_sample=8)
    m.fit(d[FEATURE_COLUMNS].astype(float),d.relevance_grade.astype(float),group=groups,verbose=False)
    return m

def score_pairs(model,pairs):
    out=pairs.copy(); out["raw_score"]=-np.inf; mask=out.eligible==1
    if mask.any(): out.loc[mask,"raw_score"]=model.predict(out.loc[mask,FEATURE_COLUMNS].astype(float))
    def norm(g):
        g=g.copy(); m=g.eligible==1; vals=g.loc[m,"raw_score"]
        if len(vals):
            lo,hi=vals.min(),vals.max(); g.loc[m,"match_score"]=50.0 if np.isclose(lo,hi) else 100*(vals-lo)/(hi-lo)
        g.loc[~m,"match_score"]=0.0; return g
    out=out.groupby("event_id",group_keys=False).apply(norm,include_groups=True).reset_index(drop=True)
    out["rank"]=out.groupby("event_id")["raw_score"].rank(method="first",ascending=False)
    return out

def evaluate_ranking(model,df,ks=(5,10)):
    scored=score_pairs(model,df); res={}
    for k in ks:
        nd=[]; pr=[]; rc=[]
        for _,g in scored.groupby("event_id"):
            g=g[g.eligible==1].sort_values("raw_score",ascending=False)
            if g.empty: continue
            y=g.relevance_grade.to_numpy(float); s=g.raw_score.to_numpy(float); kk=min(k,len(g))
            try: nd.append(ndcg_score([y],[s],k=kk))
            except Exception: pass
            rel=(y>=1).astype(int); top=rel[:kk]; pr.append(float(top.mean())); rc.append(float(top.sum()/rel.sum()) if rel.sum() else 1.0)
        res[f"ndcg@{k}"]=float(np.mean(nd)) if nd else np.nan; res[f"precision@{k}"]=float(np.mean(pr)) if pr else np.nan; res[f"recall@{k}"]=float(np.mean(rc)) if rc else np.nan
    return res

def bootstrap_selection_confidence(train_df,live_pairs,top_n=5,n_boot=8,random_state=100):
    rng=np.random.default_rng(random_state); events=np.array(sorted(train_df.event_id.unique())); counts={(e,c):0 for e,c in zip(live_pairs.event_id,live_pairs.client_id)}
    for b in range(n_boot):
        sampled=rng.choice(events,size=len(events),replace=True); chunks=[]
        for j,ev in enumerate(sampled):
            ch=train_df[train_df.event_id==ev].copy(); ch["event_id"]=f"B{b}_{j}_{ev}"; chunks.append(ch)
        m=fit_ranker(pd.concat(chunks,ignore_index=True),random_state+b,n_estimators=100); sc=score_pairs(m,live_pairs)
        for ev,g in sc.groupby("event_id"):
            for _,r in g[g.eligible==1].nlargest(top_n,"raw_score").iterrows(): counts[(ev,r.client_id)]+=1
    return pd.DataFrame([{"event_id":e,"client_id":c,"selection_confidence":v/n_boot} for (e,c),v in counts.items()])
