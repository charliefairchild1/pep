"""Strata Predict — prediction markets vertical."""
from .core import Asset
ASSETS = [
    Asset("PRES2028", "2028 US Presidential", "Politics", "general election binary outcome"),
    Asset("FED-RATE", "Fed Rate Dec 2026", "Macro", "interest rate decision FOMC"),
    Asset("AI-AGI-2030", "AGI by 2030", "Technology", "artificial general intelligence timeline"),
    Asset("CLIMATE-1.5C", "1.5°C by 2030", "Climate", "Paris agreement threshold overshoot"),
    Asset("BTC-100K", "BTC > $100K in 2026", "Crypto", "bitcoin price threshold"),
    Asset("RECESSION-2027", "US Recession by 2027", "Macro", "NBER recession determination"),
    Asset("MARS-2030", "Human on Mars by 2030", "Space", "crewed Mars mission SpaceX"),
    Asset("NUCLEAR-PLANT", "New US Nuclear Plant", "Energy", "nuclear construction permit"),
    Asset("MERGER-MSFT", "MSFT Major Acquisition", "Corporate", "Microsoft M&A > $10B"),
    Asset("PANDEMIC-2027", "New Pandemic by 2027", "Health", "WHO pandemic declaration"),
]
ARCHETYPES = {"news_jump": {}, "poll_mean_reversion": {}, "late_resolution_collapse": {}, "cross_venue_arb": {}}
