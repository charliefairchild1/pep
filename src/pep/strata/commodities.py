"""Strata Commodities — futures vertical."""
from .core import Asset
ASSETS = [
    Asset("CL", "Crude Oil (WTI)", "Energy", "benchmark oil OPEC supply demand"),
    Asset("NG", "Natural Gas", "Energy", "heating power weather driven"),
    Asset("GC", "Gold", "Precious", "safe haven central banks inflation"),
    Asset("SI", "Silver", "Precious", "industrial + monetary dual use"),
    Asset("HG", "Copper", "Industrial", "Dr Copper economic indicator"),
    Asset("W", "Wheat", "Agriculture", "food staple weather geopolitics"),
    Asset("C", "Corn", "Agriculture", "ethanol feed grain USDA"),
    Asset("S", "Soybeans", "Agriculture", "China demand crush spread"),
    Asset("LI", "Lithium", "Strategic", "EV battery supply chain"),
    Asset("UX", "Uranium", "Strategic", "nuclear renaissance supply deficit"),
]
ARCHETYPES = {"weather_spike": {}, "opec_announcement": {}, "shipping_disruption": {}, "seasonal_flip": {}, "stockpile_shift": {}}
