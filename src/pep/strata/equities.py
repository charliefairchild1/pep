"""Strata Equities — the shipping vertical."""
from .core import Asset
ASSETS = [
    Asset("AAPL", "Apple", "Tech", "consumer tech hardware iPhone services"),
    Asset("MSFT", "Microsoft", "Tech", "software cloud Azure enterprise"),
    Asset("NVDA", "Nvidia", "Tech", "GPU semiconductors AI datacenter"),
    Asset("JPM", "JPMorgan", "Financial", "bank investment consumer"),
    Asset("XOM", "Exxon", "Energy", "oil gas upstream downstream"),
    Asset("JNJ", "J&J", "Healthcare", "pharmaceuticals medical devices"),
    Asset("GLD", "Gold ETF", "Safe haven", "precious metal inflation hedge"),
    Asset("SPY", "S&P 500 ETF", "Index", "broad market passive"),
    Asset("BTC", "Bitcoin", "Crypto", "digital gold decentralized volatile"),
    Asset("TSLA", "Tesla", "Consumer", "EV automotive energy storage"),
]
