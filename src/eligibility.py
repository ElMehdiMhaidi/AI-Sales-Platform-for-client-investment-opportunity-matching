from __future__ import annotations
from .utils import norm_token, pipe_to_set

ASSET_COMPAT={"volatility":{"volatility","equity"},"credit":{"credit","rates"}}

def evaluate_eligibility(event, client):
    asset=norm_token(event.get("asset_class_std",event.get("asset_class","")))
    allowed=pipe_to_set(client.get("allowed_asset_classes","")) or pipe_to_set(client.get("typical_asset_classes",""))
    blocked=pipe_to_set(client.get("blocked_asset_classes",""))
    if asset in blocked: return False,f"blocked asset class: {asset}"
    if allowed:
        candidates=ASSET_COMPAT.get(asset,{asset})
        if not candidates & allowed: return False,f"asset class not in allowed universe: {asset}"
    er=pipe_to_set(event.get("event_regions","")); ec=pipe_to_set(event.get("event_currencies","")); et=pipe_to_set(event.get("sales_theme_tags",""))
    br=pipe_to_set(client.get("blocked_regions","")); bc=pipe_to_set(client.get("blocked_currencies","")); bt=pipe_to_set(client.get("blocked_themes",""))
    if er & br: return False,f"blocked region: {', '.join(sorted(er&br))}"
    if ec & bc: return False,f"blocked currency: {', '.join(sorted(ec&bc))}"
    if et & bt: return False,f"blocked theme: {', '.join(sorted(et&bt))}"
    strength=float(event.get("strength",0) or 0); limit=float(client.get("effective_max_event_strength",3.0) or 3.0)
    if strength>limit: return False,f"event strength {strength:.2f} exceeds client limit {limit:.2f}"
    return True,"eligible"
