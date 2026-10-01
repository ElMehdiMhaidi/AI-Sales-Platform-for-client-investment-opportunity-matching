from __future__ import annotations

from urllib.parse import urlparse

HIGH_PUBLISHERS = {
    "reuters","bloomberg","financial times","ft","the wall street journal","wall street journal","wsj",
    "federal reserve","european central bank","bank of england","bank of japan","international energy agency",
    "opec","imf","world bank","bis","ecb","fed","boe","boj",
}
MEDIUM_PUBLISHERS = {
    "cnbc","marketwatch","yahoo finance","forbes","business insider","fortune","bbc","cnn","new york times",
    "the new york times","guardian","the guardian","associated press","ap","axios","barron's","barrons",
}


def classify_source(publisher: str, url: str = "") -> str:
    p = (publisher or "").strip().lower()
    host = urlparse(url).netloc.lower().replace("www.", "") if url else ""
    if any(x in p for x in HIGH_PUBLISHERS) or any(x.replace(" ","") in host.replace(".","") for x in ["reuters","bloomberg","ft.com","wsj"]):
        return "HIGH"
    if any(x in p for x in MEDIUM_PUBLISHERS) or any(x.replace(" ","") in host.replace(".","") for x in ["cnbc","marketwatch","finance.yahoo","forbes","businessinsider","bbc","cnn"]):
        return "MEDIUM"
    return "LOW"


def aggregate_confidence(levels) -> str:
    levels = {str(x).upper() for x in levels}
    if "HIGH" in levels: return "HIGH"
    if "MEDIUM" in levels: return "MEDIUM"
    return "LOW"
