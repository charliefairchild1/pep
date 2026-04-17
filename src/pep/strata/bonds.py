"""Strata Bonds — fixed income vertical."""
from .core import Asset
ASSETS = [
    Asset("UST-2Y", "US 2Y Treasury", "Sovereign", "short duration Fed sensitive"),
    Asset("UST-10Y", "US 10Y Treasury", "Sovereign", "benchmark yield curve term premium"),
    Asset("UST-30Y", "US 30Y Treasury", "Sovereign", "long duration inflation sensitive"),
    Asset("TIPS", "TIPS (inflation)", "Sovereign", "inflation-protected real yield"),
    Asset("IG-CORP", "IG Corporate", "Credit", "investment grade spread quality"),
    Asset("HY-CORP", "HY Corporate", "Credit", "junk bonds default risk spread"),
    Asset("MBS", "Mortgage-Backed", "Securitized", "prepayment risk housing Fed"),
    Asset("MUNI", "Municipal", "Tax-exempt", "state local tax advantage"),
    Asset("EM-BOND", "EM Sovereign", "Emerging", "USD-denominated country risk"),
    Asset("CONVERT", "Convertible", "Hybrid", "equity option embedded bond"),
]
ARCHETYPES = {"yield_curve_inversion": {}, "credit_spread_blowout": {}, "downgrade_cascade": {}, "repo_stress": {}, "central_bank_pivot": {}}
