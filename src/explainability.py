from __future__ import annotations
REASONS=[("exposure_match",.08,"Relevant exposure"),("commercial_need_match",.08,"Commercial-need alignment"),("recent_need_similarity",.08,"Recent related client need"),("directional_match",.5,"Directional risk relevance"),("semantic_similarity",.15,"Strong semantic profile match"),("asset_match",.5,"Asset-class relevance"),("region_match",.5,"Regional relevance"),("currency_match",.5,"Currency relevance")]
def reasons_for_pair(row,top_k=3):
    out=[]
    for col,t,label in REASONS:
        try:v=float(row.get(col,0))
        except:v=0
        if v>=t: out.append(label)
        if len(out)>=top_k: break
    return out or ["Model-ranked opportunity"]
