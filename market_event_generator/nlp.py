from __future__ import annotations

import re
from collections import Counter
from typing import Dict, List

CATALYST_GROUPS = {
    "central-bank policy": ["fed","federal reserve","ecb","bank of england","boe","boj","bank of japan","rate hike","rate cut","monetary policy"],
    "inflation": ["inflation","cpi","prices","price pressure","pce"],
    "growth / macro": ["pmi","growth","jobs","payroll","unemployment","manufacturing","recession"],
    "geopolitical / supply risk": ["war","conflict","sanction","attack","geopolitical","disruption","shipping","supply"],
    "OPEC / oil supply": ["opec","oil output","production cut","crude supply"],
    "AI / technology demand": ["ai","artificial intelligence","semiconductor","chip","data center","datacenter"],
    "fiscal / sovereign risk": ["deficit","debt","fiscal","sovereign","budget"],
    "earnings / corporate": ["earnings","revenue","profit","guidance","forecast"],
}

SALES_THEME_MAP = {
    "Equity": ["Downside Hedging","Equity Risk Review","Sector Rotation"],
    "FX": ["Corporate FX Hedging","Currency Risk Review","Optional Hedge"],
    "Rates": ["Duration Review","Fixed-Rate Hedging","Funding Cost Review"],
    "Commodity": ["Producer/Consumer Hedging","Inflation Exposure","Commodity Risk Review"],
    "Volatility": ["Volatility Review","Downside Hedging","Option Monetization"],
    "Credit": ["Credit Spread Risk","Liquidity Review","Relative Value"],
}


def dedupe_news(news: List[Dict]) -> List[Dict]:
    seen=set(); out=[]
    for n in news:
        key=re.sub(r"\W+"," ",n.get("title","").lower()).strip()
        key=" ".join(key.split()[:12])
        if key and key not in seen:
            seen.add(key); out.append(n)
    return out


def extract_catalysts(news: List[Dict], max_items=4) -> List[str]:
    text=" ".join((n.get("title","")+" "+n.get("text","")) for n in news).lower()
    scores=[]
    for label,words in CATALYST_GROUPS.items():
        score=sum(text.count(w) for w in words)
        if score: scores.append((score,label))
    scores.sort(reverse=True)
    return [x[1] for x in scores[:max_items]]


def extractive_observation(news: List[Dict], fallback: str) -> str:
    if not news: return fallback
    # Prefer the best-quality headline; quantitative facts remain in quant_observations.
    rank={"HIGH":3,"MEDIUM":2,"LOW":1}
    best=max(news,key=lambda n:(rank.get(str(n.get("source_confidence","LOW")).upper(),0),len(n.get("title",""))))
    title=re.sub(r"\s+-\s+[^-]+$","",best.get("title","")).strip()
    return title or fallback


def build_theme(asset_class: str, underlying: str, signal: Dict) -> str:
    d=signal.get("direction","FLAT")
    if asset_class=="Rates": return f"{underlying} yields move {'higher' if d=='UP' else 'lower' if d=='DOWN' else 'sideways'}"
    if asset_class=="Volatility": return f"{underlying} volatility {'spike' if d=='UP' else 'compression' if d=='DOWN' else 'stability'}"
    if asset_class=="Commodity": return f"{underlying} commodity move {'higher' if d=='UP' else 'lower' if d=='DOWN' else 'sideways'}"
    if asset_class=="FX": return f"{underlying} FX move {'higher' if d=='UP' else 'lower' if d=='DOWN' else 'sideways'}"
    return f"{underlying} market move {'higher' if d=='UP' else 'lower' if d=='DOWN' else 'sideways'}"


def sales_themes(asset_class: str, signal: Dict) -> List[str]:
    themes=list(SALES_THEME_MAP.get(asset_class,["Risk Review"]))
    if asset_class=="Equity" and signal.get("direction")=="UP": themes=["Equity Upside","Sector Rotation","Risk Review"]
    if asset_class=="Rates" and signal.get("direction")=="DOWN": themes=["Duration Review","Yield Lock-In","Funding Cost Review"]
    return themes
