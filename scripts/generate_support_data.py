from __future__ import annotations

from pathlib import Path
import random
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; RNG=random.Random(42)

archetypes=[
    ('Large Bank','equity|rates|fx|credit|volatility','global|europe|us|uk','usd|eur|gbp|jpy','equity|rates|fx|credit|volatility','downside_hedging|duration_review|fixed-rate_hedging|corporate_fx_hedging|yield_enhancement','high',3.2),
    ('Regional Bank','rates|fx|credit','europe|uk','eur|gbp|usd','eur_rates|gbp_rates|eur_credit|fx','duration_review|fixed-rate_hedging|yield_lock-in|corporate_fx_hedging','medium',2.5),
    ('Global Asset Manager','equity|rates|fx|credit|commodity|volatility','global|europe|us|uk|japan','usd|eur|gbp|jpy','equity|rates|credit|fx|commodity|volatility','downside_hedging|risk_review|duration_review|recovery_participation|optional_hedge','high',3.2),
    ('Pension Fund','equity|rates|credit','europe|us|uk','eur|usd|gbp','duration|investment_grade|europe_equity|us_equity','duration_review|capital_preservation|downside_hedging|yield_lock-in','low',1.9),
    ('Insurance Company','rates|credit|equity|fx','europe|us|uk','eur|usd|gbp','duration|investment_grade|fx|equity','duration_review|capital_preservation|fixed-rate_hedging|fx_hedging','low',2.0),
    ('Macro Hedge Fund','equity|rates|fx|credit|commodity|volatility','global|europe|us|japan','usd|eur|gbp|jpy','equity|rates|fx|credit|commodity|volatility','relative_value|option_monetization|risk_review|optional_hedge|commodity_risk_review','very_high',3.5),
    ('Private Bank','equity|rates|fx|credit|volatility|commodity','global|europe|us|uk','eur|usd|gbp|chf','equity|rates|fx|credit|volatility|gold','yield_enhancement|option_monetization|downside_hedging|capital_preservation|recovery_participation','medium',2.7),
    ('Family Office','equity|rates|fx|credit|commodity','global|europe|us|uk','eur|usd|gbp|chf','equity|rates|fx|commodity|credit','capital_preservation|yield_enhancement|downside_hedging|commodity_risk_review|optional_hedge','medium',2.5),
    ('Large Corporate','fx|rates|commodity','global|europe|us|asia','eur|usd|gbp|jpy','fx|rates|commodity|energy','corporate_fx_hedging|fixed-rate_hedging|producer/consumer_hedging|commodity_risk_review|yield_lock-in','medium',2.8),
    ('Mid-Cap Corporate','fx|rates|commodity','europe|uk|us','eur|usd|gbp','fx|rates|commodity|energy','corporate_fx_hedging|fixed-rate_hedging|producer/consumer_hedging','low',2.1),
]
arch=[]
for a,assets,regions,ccy,exp,needs,risk,mx in archetypes:
    arch.append(dict(archetype=a,typical_asset_classes=assets,typical_regions=regions,typical_currencies=ccy,typical_exposures=exp,typical_needs=needs,risk_capacity=risk,archetype_max_event_strength=mx,default_derivatives_allowed=True,typical_restrictions=''))
pd.DataFrame(arch).to_csv(DATA/'archetypes.csv',index=False)

clients=[]
for i in range(60):
    ar=arch[i%len(arch)]; assets=ar['typical_asset_classes'].split('|'); needs=ar['typical_needs'].split('|'); exps=ar['typical_exposures'].split('|')
    use_assets=RNG.sample(assets,max(1,RNG.randint(max(1,len(assets)-2),len(assets))))
    use_needs=RNG.sample(needs,max(1,RNG.randint(1,min(3,len(needs)))))
    use_exp=set(RNG.sample(exps,max(1,RNG.randint(1,len(exps)))))
    if 'equity' in use_assets: use_exp.add(RNG.choice(['us_equity','europe_equity','technology','sp500','eurostoxx50']))
    if 'rates' in use_assets: use_exp.add(RNG.choice(['usd_rates','eur_rates','duration','10y']))
    if 'fx' in use_assets: use_exp.add(RNG.choice(['eurusd','gbpusd','usdjpy','fx']))
    if 'commodity' in use_assets: use_exp.add(RNG.choice(['oil','gold','copper','commodity']))
    adverse_down=[]; adverse_up=[]
    if 'equity' in use_assets: adverse_down=['equity']
    if 'rates' in use_assets: adverse_up=['rates','us10y','us30y']
    if 'commodity' in use_assets and 'Corporate' in ar['archetype']: adverse_up.append('brent')
    clients.append(dict(client_id=f'CL_{i+1:03d}',client_name=f'Synthetic {ar["archetype"]} {i+1:02d}',client_type=ar['archetype'],archetype=ar['archetype'],size_bucket=RNG.choice(['mid','large']),regions=ar['typical_regions'],currencies=ar['typical_currencies'],asset_classes='|'.join(use_assets),objectives='|'.join(use_needs),exposures='|'.join(sorted(use_exp)),hedging_needs='|'.join(use_needs),risk_profile=ar['risk_capacity'],derivatives_allowed=True,allowed_asset_classes='|'.join(use_assets),blocked_asset_classes='',blocked_regions='',blocked_currencies='',blocked_themes='',adverse_if_up='|'.join(adverse_up),adverse_if_down='|'.join(adverse_down),max_event_strength=round(float(ar['archetype_max_event_strength'])+RNG.uniform(-.2,.2),2),profile_text=f"Synthetic {ar['archetype']} active in {', '.join(use_assets)} with priorities {', '.join(use_needs)}."))
pd.DataFrame(clients).to_csv(DATA/'clients.csv',index=False)

# Ambiguous recent history
rows=[]; base=pd.Timestamp.today().normalize()
for c in clients:
    assets=c['asset_classes'].split('|'); needs=c['objectives'].split('|')
    for j in range(RNG.randint(4,8)):
        dt=base-pd.Timedelta(days=RNG.randint(5,420)); need=RNG.choice(needs if RNG.random()<.72 else ['risk_review','yield_enhancement','capital_preservation','relative_value']); asset=RNG.choice(assets)
        status=RNG.choice(['discussed','quoted','watchlist','deferred','declined','no_action','follow_up'])
        text=f"Conversation {'explicitly raised' if RNG.random()<.6 else 'suggested possible interest in'} {need.replace('_',' ')} in {asset}; status={status}."
        rows.append(dict(client_id=c['client_id'],date=dt.date(),need=need.replace('_',' '),asset_class=asset,underlying=asset.upper(),product_family='review',objective=need,need_text=text,status=status))
pd.DataFrame(rows).to_csv(DATA/'client_history.csv',index=False)

# Synthetic training events kept separate from live market_events.
assets=[('Equity','SP500'),('Equity','EUROSTOXX50'),('Rates','US10Y'),('FX','EURUSD'),('FX','USDJPY'),('Commodity','BRENT'),('Commodity','GOLD'),('Volatility','VIX')]
train=[]
for i in range(24):
    ac,u=assets[i%len(assets)]; direction='UP' if i%3 else 'DOWN'; strength=round(1.2+(i%8)*.25,2)
    sales={'Equity':['Downside Hedging','Risk Review'],'Rates':['Duration Review','Fixed-Rate Hedging'],'FX':['Corporate FX Hedging','Currency Risk Review'],'Commodity':['Commodity Risk Review','Inflation Exposure'],'Volatility':['Volatility Review','Downside Hedging']}[ac]
    train.append(dict(event_id=f'TR_{i+1:04d}',timestamp=(base-pd.Timedelta(days=30+i*8)).date(),asset_class=ac,underlying=u,signal_type=f'{ac.upper()}_MOVE_{direction}',direction=direction,strength=strength,theme=f'{u} training market move',observation=f'{u} generated a representative {direction.lower()} market event.',quant_observations=str({'zscore_5d':round(((-1 if direction=='DOWN' else 1)*strength),2)}),catalysts=str(['macro catalyst','market repricing']),source_ids=str([f'TRAIN_SRC_{i+1:03d}']),confidence='HIGH' if i%2 else 'MEDIUM',sales_themes=str(sales),market_snapshot_id=f'MS_TR_{i+1:04d}',quant_signal_id=f'QS_TR_{i+1:04d}'))
pd.DataFrame(train).to_csv(DATA/'training_events.csv',index=False)
print('support data written')
