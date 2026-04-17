"""Strata FX — foreign exchange vertical."""
from .core import Asset
ASSETS = [
    Asset("EURUSD", "EUR/USD", "Major", "euro dollar most liquid pair"),
    Asset("GBPUSD", "GBP/USD", "Major", "cable sterling Brexit sensitivity"),
    Asset("USDJPY", "USD/JPY", "Major", "carry trade BoJ intervention"),
    Asset("USDCHF", "USD/CHF", "Safe haven", "Swiss franc flight to safety"),
    Asset("AUDUSD", "AUD/USD", "Commodity", "Aussie iron ore China proxy"),
    Asset("USDCAD", "USD/CAD", "Commodity", "loonie oil correlation"),
    Asset("NZDUSD", "NZD/USD", "Commodity", "kiwi dairy exports"),
    Asset("EURGBP", "EUR/GBP", "Cross", "Brexit trade EU-UK divergence"),
    Asset("USDCNY", "USD/CNY", "EM", "managed float PBoC intervention"),
    Asset("USDMXN", "USD/MXN", "EM", "nearshoring carry high yield"),
]
ARCHETYPES = {"carry_unwind": {}, "central_bank_intervention": {}, "risk_off_flight": {}, "peg_break": {}, "rebalancing": {}}
