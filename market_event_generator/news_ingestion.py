from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Dict, List
from urllib.parse import quote_plus

import feedparser
import requests
from bs4 import BeautifulSoup

from .config import MAX_NEWS_PER_INSTRUMENT, NEWS_LOOKBACK_DAYS
from .source_quality import classify_source

UA = "Mozilla/5.0 (compatible; MarketEventResearchBot/1.0; personal research project)"


def _publisher(entry) -> str:
    try:
        if getattr(entry,"source",None) and entry.source.get("title"):
            return entry.source.get("title")
    except Exception:
        pass
    title=str(entry.get("title",""))
    if " - " in title: return title.rsplit(" - ",1)[-1].strip()
    return "Unknown"


def _clean_html(text: str) -> str:
    return BeautifulSoup(text or "","html.parser").get_text(" ",strip=True)


def _fetch_page_text(url: str, timeout=6) -> str:
    try:
        r=requests.get(url,headers={"User-Agent":UA},timeout=timeout,allow_redirects=True)
        r.raise_for_status(); soup=BeautifulSoup(r.text,"lxml")
        for x in soup(["script","style","nav","footer","header","aside"]): x.decompose()
        paras=[p.get_text(" ",strip=True) for p in soup.find_all("p")]
        text=" ".join(x for x in paras if len(x)>40)
        return text[:12000]
    except Exception:
        return ""


def fetch_google_news(query: str, max_items: int = MAX_NEWS_PER_INSTRUMENT) -> List[Dict]:
    q=f"{query} when:{NEWS_LOOKBACK_DAYS}d"
    url=f"https://news.google.com/rss/search?q={quote_plus(q)}&hl=en-US&gl=US&ceid=US:en"
    feed=feedparser.parse(url)
    rows=[]
    for e in feed.entries[:max_items]:
        title=str(e.get("title","")); link=str(e.get("link","")); pub=_publisher(e)
        summary=_clean_html(e.get("summary","") or e.get("description",""))
        body=_fetch_page_text(link, timeout=3) if link and len(rows) < 1 else ""
        published=str(e.get("published",e.get("updated","")))
        sid="SRC_"+hashlib.sha1((title+link).encode("utf-8","ignore")).hexdigest()[:10].upper()
        rows.append({"source_id":sid,"publisher":pub,"published_at":published,"source_type":"news","title":title,"url":link,
                     "source_confidence":classify_source(pub,link),"text":body or summary or title})
    return rows


def yahoo_market_source(ticker: str, underlying: str) -> Dict:
    sid="YF_"+re.sub(r"[^A-Z0-9]","",underlying.upper())
    return {"source_id":sid,"publisher":"Yahoo Finance","published_at":datetime.now(timezone.utc).isoformat(),"source_type":"market_data",
            "title":f"Yahoo Finance daily market data — {underlying} ({ticker})","url":f"https://finance.yahoo.com/quote/{ticker}",
            "source_confidence":"MEDIUM","text":"Daily OHLCV market data used for the quantitative signal."}
