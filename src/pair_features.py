from __future__ import annotations
import numpy as np
import pandas as pd
from .eligibility import evaluate_eligibility
from .utils import cosine,jaccard,norm_token,overlap_any,pipe_to_set

FEATURE_COLUMNS=["asset_match","exposure_match","region_match","currency_match","commercial_need_match","directional_match","semantic_similarity","recent_need_similarity","recency_weight","risk_headroom","archetype_relevance"]

def _mean(vals):
    vals=[float(x) for x in vals if x is not None and not np.isnan(x)]
    return float(np.mean(vals)) if vals else 0.0

def _asset(event_asset, aset):
    if not aset: return 0.0
    if event_asset=="volatility": return float(bool({"volatility","equity"}&aset))
    if event_asset=="credit": return float(bool({"credit","rates"}&aset))
    return float(event_asset in aset)

def _direction(event,client):
    d=int(event.get("direction_std",0)); tags={norm_token(event.get("underlying_std","")),norm_token(event.get("asset_class_std",""))}
    up=pipe_to_set(client.get("adverse_if_up","")); down=pipe_to_set(client.get("adverse_if_down",""))
    if d>0: return float(bool(tags&up))
    if d<0: return float(bool(tags&down))
    return 0.0

def build_pair_features(events,clients,event_embeddings,client_embeddings,recent_embeddings):
    rows=[]
    for _,e in events.iterrows():
        ea=norm_token(e["asset_class_std"]); ee=pipe_to_set(e.get("event_exposure_tags",""))|{norm_token(e.get("underlying_std","")),ea}
        er=pipe_to_set(e.get("event_regions","")); ec=pipe_to_set(e.get("event_currencies","")); en=pipe_to_set(e.get("sales_theme_tags",""))
        for _,c in clients.iterrows():
            eligible,reason=evaluate_eligibility(e,c)
            ca=pipe_to_set(c.get("asset_classes","")); aa=pipe_to_set(c.get("typical_asset_classes",""))
            asset_match=_mean([_asset(ea,ca),_asset(ea,aa)])
            ce=pipe_to_set(c.get("exposures","")); ae=pipe_to_set(c.get("typical_exposures",""))
            exposure_match=_mean([jaccard(ee,ce),jaccard(ee,ae)])
            needs=pipe_to_set(c.get("objectives",""))|pipe_to_set(c.get("hedging_needs","")); an=pipe_to_set(c.get("typical_needs",""))
            need_match=_mean([jaccard(en,needs),jaccard(en,an)])
            sem=max(0.0,cosine(event_embeddings[e.event_id],client_embeddings[c.client_id]))
            recent=max(0.0,cosine(event_embeddings[e.event_id],recent_embeddings[c.client_id]))*float(c.get("recency_weight",0))
            strength=float(e.get("strength",0)); limit=max(float(c.get("effective_max_event_strength",3)),1e-6)
            rows.append({"event_id":e.event_id,"client_id":c.client_id,"eligible":int(eligible),"eligibility_reason":reason,
                         "asset_match":asset_match,"exposure_match":exposure_match,"region_match":overlap_any(er,pipe_to_set(c.get("regions",""))) if er else 0.0,
                         "currency_match":overlap_any(ec,pipe_to_set(c.get("currencies",""))) if ec else 0.0,"commercial_need_match":need_match,
                         "directional_match":_direction(e,c),"semantic_similarity":sem,"recent_need_similarity":recent,"recency_weight":float(c.get("recency_weight",0)),
                         "risk_headroom":max(0.0,min(1.0,(limit-strength)/limit)) if eligible else 0.0,
                         "archetype_relevance":_mean([_asset(ea,aa),jaccard(ee,ae),jaccard(en,an)])})
    return pd.DataFrame(rows)
