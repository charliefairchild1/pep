"""Strata Crypto — cryptocurrency vertical."""
from .core import Asset
ASSETS = [
    Asset("BTC", "Bitcoin", "L1", "store of value digital gold halving cycle"),
    Asset("ETH", "Ethereum", "L1", "smart contracts DeFi merge staking"),
    Asset("SOL", "Solana", "L1", "high throughput low fees NFTs"),
    Asset("BNB", "BNB", "Exchange", "Binance ecosystem utility token"),
    Asset("XRP", "Ripple", "Payment", "cross-border settlement banks"),
    Asset("ADA", "Cardano", "L1", "academic peer-reviewed slow rollout"),
    Asset("DOGE", "Dogecoin", "Meme", "community driven Elon social sentiment"),
    Asset("AVAX", "Avalanche", "L1", "subnets institutional DeFi"),
    Asset("LINK", "Chainlink", "Oracle", "price feeds real-world data"),
    Asset("UNI", "Uniswap", "DeFi", "AMM decentralized exchange governance"),
]
ARCHETYPES = {"pump_and_dump": {}, "rug_pull": {}, "listing_effect": {}, "halving_cycle": {}, "mev_sandwich": {}}
