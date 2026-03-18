import os
import time
import random
from datetime import datetime, timedelta, timezone
from flask import Flask, jsonify, request
from flask_cors import CORS

# Create Flask app
app = Flask(__name__)
CORS(app)

# Your Quotex login details
QUOTEX_EMAIL = "90d096681b@emailax.pro"
QUOTEX_PASSWORD = "Rakib1@@"

# ============================================
# COMPLETE ASSET DATABASE - 100+ PAIRS
# ============================================
ASSETS = {
    # ===== Forex (Real Market) =====
    "EURUSD": {"symbol_id": 101, "name": "EUR/USD", "base_price": 1.0876, "group": "Forex Real", "volatility": 0.002},
    "GBPUSD": {"symbol_id": 102, "name": "GBP/USD", "base_price": 1.2645, "group": "Forex Real", "volatility": 0.002},
    "USDJPY": {"symbol_id": 103, "name": "USD/JPY", "base_price": 148.32, "group": "Forex Real", "volatility": 0.003},
    "USDCHF": {"symbol_id": 104, "name": "USD/CHF", "base_price": 0.8765, "group": "Forex Real", "volatility": 0.002},
    "AUDUSD": {"symbol_id": 105, "name": "AUD/USD", "base_price": 0.6578, "group": "Forex Real", "volatility": 0.002},
    "USDCAD": {"symbol_id": 106, "name": "USD/CAD", "base_price": 1.3489, "group": "Forex Real", "volatility": 0.002},
    "EURGBP": {"symbol_id": 107, "name": "EUR/GBP", "base_price": 0.8592, "group": "Forex Real", "volatility": 0.0015},
    "EURJPY": {"symbol_id": 108, "name": "EUR/JPY", "base_price": 161.25, "group": "Forex Real", "volatility": 0.003},
    "GBPJPY": {"symbol_id": 109, "name": "GBP/JPY", "base_price": 187.45, "group": "Forex Real", "volatility": 0.003},
    "AUDJPY": {"symbol_id": 110, "name": "AUD/JPY", "base_price": 97.58, "group": "Forex Real", "volatility": 0.003},
    "EURCHF": {"symbol_id": 111, "name": "EUR/CHF", "base_price": 0.9532, "group": "Forex Real", "volatility": 0.0015},
    "GBPCHF": {"symbol_id": 112, "name": "GBP/CHF", "base_price": 1.1085, "group": "Forex Real", "volatility": 0.002},
    "AUDCAD": {"symbol_id": 113, "name": "AUD/CAD", "base_price": 0.8876, "group": "Forex Real", "volatility": 0.002},
    "AUDNZD": {"symbol_id": 114, "name": "AUD/NZD", "base_price": 1.0785, "group": "Forex Real", "volatility": 0.0015},
    "CADJPY": {"symbol_id": 115, "name": "CAD/JPY", "base_price": 109.95, "group": "Forex Real", "volatility": 0.003},
    "CHFJPY": {"symbol_id": 116, "name": "CHF/JPY", "base_price": 169.23, "group": "Forex Real", "volatility": 0.003},
    "EURAUD": {"symbol_id": 117, "name": "EUR/AUD", "base_price": 1.6532, "group": "Forex Real", "volatility": 0.002},
    "EURCAD": {"symbol_id": 118, "name": "EUR/CAD", "base_price": 1.4678, "group": "Forex Real", "volatility": 0.002},
    "GBPAUD": {"symbol_id": 119, "name": "GBP/AUD", "base_price": 1.9234, "group": "Forex Real", "volatility": 0.002},
    "GBPCAD": {"symbol_id": 120, "name": "GBP/CAD", "base_price": 1.7056, "group": "Forex Real", "volatility": 0.002},

    # ===== Forex OTC Pairs =====
    "EURUSD_otc": {"symbol_id": 201, "name": "EUR/USD (OTC)", "base_price": 1.0876, "group": "Forex OTC",
                   "volatility": 0.0025},
    "GBPUSD_otc": {"symbol_id": 202, "name": "GBP/USD (OTC)", "base_price": 1.2645, "group": "Forex OTC",
                   "volatility": 0.0025},
    "USDJPY_otc": {"symbol_id": 203, "name": "USD/JPY (OTC)", "base_price": 148.32, "group": "Forex OTC",
                   "volatility": 0.0035},
    "USDCHF_otc": {"symbol_id": 204, "name": "USD/CHF (OTC)", "base_price": 0.8765, "group": "Forex OTC",
                   "volatility": 0.0025},
    "AUDUSD_otc": {"symbol_id": 205, "name": "AUD/USD (OTC)", "base_price": 0.6578, "group": "Forex OTC",
                   "volatility": 0.0025},
    "USDCAD_otc": {"symbol_id": 206, "name": "USD/CAD (OTC)", "base_price": 1.3489, "group": "Forex OTC",
                   "volatility": 0.0025},
    "EURGBP_otc": {"symbol_id": 207, "name": "EUR/GBP (OTC)", "base_price": 0.8592, "group": "Forex OTC",
                   "volatility": 0.002},
    "EURNZD_otc": {"symbol_id": 208, "name": "EUR/NZD (OTC)", "base_price": 1.7923, "group": "Forex OTC",
                   "volatility": 0.0025},
    "EURJPY_otc": {"symbol_id": 209, "name": "EUR/JPY (OTC)", "base_price": 161.25, "group": "Forex OTC",
                   "volatility": 0.0035},
    "GBPJPY_otc": {"symbol_id": 210, "name": "GBP/JPY (OTC)", "base_price": 187.45, "group": "Forex OTC",
                   "volatility": 0.0035},
    "AUDJPY_otc": {"symbol_id": 211, "name": "AUD/JPY (OTC)", "base_price": 97.58, "group": "Forex OTC",
                   "volatility": 0.0035},
    "EURCHF_otc": {"symbol_id": 212, "name": "EUR/CHF (OTC)", "base_price": 0.9532, "group": "Forex OTC",
                   "volatility": 0.002},
    "EURSGD_otc": {"symbol_id": 213, "name": "EUR/SGD (OTC)", "base_price": 1.4523, "group": "Forex OTC",
                   "volatility": 0.002},
    "GBPCHF_otc": {"symbol_id": 214, "name": "GBP/CHF (OTC)", "base_price": 1.1085, "group": "Forex OTC",
                   "volatility": 0.0025},
    "NZDUSD_otc": {"symbol_id": 215, "name": "NZD/USD (OTC)", "base_price": 0.6098, "group": "Forex OTC",
                   "volatility": 0.0025},
    "NZDCHF_otc": {"symbol_id": 216, "name": "NZD/CHF (OTC)", "base_price": 0.5342, "group": "Forex OTC",
                   "volatility": 0.002},
    "NZDCAD_otc": {"symbol_id": 217, "name": "NZD/CAD (OTC)", "base_price": 0.8223, "group": "Forex OTC",
                   "volatility": 0.002},
    "NZDJPY_otc": {"symbol_id": 218, "name": "NZD/JPY (OTC)", "base_price": 90.45, "group": "Forex OTC",
                   "volatility": 0.0035},
    "AUDCAD_otc": {"symbol_id": 219, "name": "AUD/CAD (OTC)", "base_price": 0.8876, "group": "Forex OTC",
                   "volatility": 0.0025},
    "AUDNZD_otc": {"symbol_id": 220, "name": "AUD/NZD (OTC)", "base_price": 1.0785, "group": "Forex OTC",
                   "volatility": 0.002},
    "CADJPY_otc": {"symbol_id": 221, "name": "CAD/JPY (OTC)", "base_price": 109.95, "group": "Forex OTC",
                   "volatility": 0.0035},
    "CHFJPY_otc": {"symbol_id": 222, "name": "CHF/JPY (OTC)", "base_price": 169.23, "group": "Forex OTC",
                   "volatility": 0.0035},
    "EURAUD_otc": {"symbol_id": 223, "name": "EUR/AUD (OTC)", "base_price": 1.6532, "group": "Forex OTC",
                   "volatility": 0.0025},
    "EURCAD_otc": {"symbol_id": 224, "name": "EUR/CAD (OTC)", "base_price": 1.4678, "group": "Forex OTC",
                   "volatility": 0.0025},
    "GBPAUD_otc": {"symbol_id": 225, "name": "GBP/AUD (OTC)", "base_price": 1.9234, "group": "Forex OTC",
                   "volatility": 0.0025},
    "GBPNZD_otc": {"symbol_id": 226, "name": "GBP/NZD (OTC)", "base_price": 2.0745, "group": "Forex OTC",
                   "volatility": 0.0025},
    "GBPCAD_otc": {"symbol_id": 227, "name": "GBP/CAD (OTC)", "base_price": 1.7056, "group": "Forex OTC",
                   "volatility": 0.0025},
    "USDBDT_otc": {"symbol_id": 228, "name": "USD/BDT (OTC)", "base_price": 109.50, "group": "Forex OTC",
                   "volatility": 0.004},
    "BRLUSD_otc": {"symbol_id": 332, "name": "USD/BRL (OTC)", "base_price": 0.1896, "group": "Forex OTC",
                   "volatility": 0.004},
    "USDINR_otc": {"symbol_id": 229, "name": "USD/INR (OTC)", "base_price": 83.25, "group": "Forex OTC",
                   "volatility": 0.003},
    "USDARS_otc": {"symbol_id": 230, "name": "USD/ARS (OTC)", "base_price": 870.25, "group": "Forex OTC",
                   "volatility": 0.005},
    "USDPHP_otc": {"symbol_id": 231, "name": "USD/PHP (OTC)", "base_price": 56.35, "group": "Forex OTC",
                   "volatility": 0.003},
    "USDPKR_otc": {"symbol_id": 232, "name": "USD/PKR (OTC)", "base_price": 278.50, "group": "Forex OTC",
                   "volatility": 0.004},
    "USDMXN_otc": {"symbol_id": 233, "name": "USD/MXN (OTC)", "base_price": 17.25, "group": "Forex OTC",
                   "volatility": 0.004},
    "USDCOP_otc": {"symbol_id": 234, "name": "USD/COP (OTC)", "base_price": 3925.50, "group": "Forex OTC",
                   "volatility": 0.005},
    "USDEGP_otc": {"symbol_id": 235, "name": "USD/EGP (OTC)", "base_price": 47.80, "group": "Forex OTC",
                   "volatility": 0.003},
    "USDTRY_otc": {"symbol_id": 236, "name": "USD/TRY (OTC)", "base_price": 32.45, "group": "Forex OTC",
                   "volatility": 0.005},
    "USDDZD_otc": {"symbol_id": 237, "name": "USD/DZD (OTC)", "base_price": 134.50, "group": "Forex OTC",
                   "volatility": 0.003},
    "USDIDR_otc": {"symbol_id": 238, "name": "USD/IDR (OTC)", "base_price": 15750, "group": "Forex OTC",
                   "volatility": 0.004},
    "USDZAR_otc": {"symbol_id": 239, "name": "USD/ZAR (OTC)", "base_price": 18.95, "group": "Forex OTC",
                   "volatility": 0.005},

    # ===== Commodities (Real Market) =====
    "XAUUSD": {"symbol_id": 301, "name": "Gold", "base_price": 2150.50, "group": "Commodities Real",
               "volatility": 0.008},
    "XAGUSD": {"symbol_id": 302, "name": "Silver", "base_price": 25.75, "group": "Commodities Real",
               "volatility": 0.01},
    "XBRUSD": {"symbol_id": 303, "name": "Brent Oil", "base_price": 85.30, "group": "Commodities Real",
               "volatility": 0.015},
    "XTIUSD": {"symbol_id": 304, "name": "WTI Oil", "base_price": 81.20, "group": "Commodities Real",
               "volatility": 0.015},
    "NATGAS": {"symbol_id": 305, "name": "Natural Gas", "base_price": 2.75, "group": "Commodities Real",
               "volatility": 0.02},

    # ===== Commodities OTC =====
    "UKBrent_otc": {"symbol_id": 306, "name": "UK Brent Oil (OTC)", "base_price": 85.30, "group": "Commodities OTC",
                    "volatility": 0.018},
    "USCrude_otc": {"symbol_id": 307, "name": "US Crude Oil (OTC)", "base_price": 81.20, "group": "Commodities OTC",
                    "volatility": 0.018},
    "XAUUSD_otc": {"symbol_id": 308, "name": "Gold (OTC)", "base_price": 2150.50, "group": "Commodities OTC",
                   "volatility": 0.01},
    "XAGUSD_otc": {"symbol_id": 309, "name": "Silver (OTC)", "base_price": 25.75, "group": "Commodities OTC",
                   "volatility": 0.012},

    # ===== Cryptocurrencies =====
    "BTCUSD_otc": {"symbol_id": 401, "name": "Bitcoin (OTC)", "base_price": 65400, "group": "Crypto",
                   "volatility": 0.025},
    "ARBUSD_otc": {"symbol_id": 402, "name": "Arbitrum (OTC)", "base_price": 1.85, "group": "Crypto",
                   "volatility": 0.03},
    "AXIUSD_otc": {"symbol_id": 403, "name": "Axie Infinity (OTC)", "base_price": 8.75, "group": "Crypto",
                   "volatility": 0.03},
    "HAMUSD_otc": {"symbol_id": 404, "name": "Hamster (OTC)", "base_price": 0.0045, "group": "Crypto",
                   "volatility": 0.04},
    "SHIUSD_otc": {"symbol_id": 405, "name": "Shiba Inu (OTC)", "base_price": 0.000024, "group": "Crypto",
                   "volatility": 0.04},
    "ETHUSD_otc": {"symbol_id": 406, "name": "Ethereum (OTC)", "base_price": 3450, "group": "Crypto",
                   "volatility": 0.022},
    "CRLUSD_otc": {"symbol_id": 407, "name": "Cardano (OTC)", "base_price": 0.58, "group": "Crypto",
                   "volatility": 0.03},
    "BNBUSD_otc": {"symbol_id": 408, "name": "Binance Coin (OTC)", "base_price": 410, "group": "Crypto",
                   "volatility": 0.022},
    "XRPUSD_otc": {"symbol_id": 409, "name": "Ripple (OTC)", "base_price": 0.62, "group": "Crypto", "volatility": 0.03},
    "LTCUSD_otc": {"symbol_id": 410, "name": "Litecoin (OTC)", "base_price": 85.50, "group": "Crypto",
                   "volatility": 0.025},
    "DOGUSD_otc": {"symbol_id": 411, "name": "Dogecoin (OTC)", "base_price": 0.15, "group": "Crypto",
                   "volatility": 0.035},
    "TRXUSD_otc": {"symbol_id": 412, "name": "TRON (OTC)", "base_price": 0.12, "group": "Crypto", "volatility": 0.03},
    "PEPUSD_otc": {"symbol_id": 413, "name": "Pepe (OTC)", "base_price": 0.0000085, "group": "Crypto",
                   "volatility": 0.045},
    "GALUSD_otc": {"symbol_id": 414, "name": "Gala (OTC)", "base_price": 0.035, "group": "Crypto", "volatility": 0.035},
    "TRUUSD_otc": {"symbol_id": 415, "name": "Trump (OTC)", "base_price": 2.45, "group": "Crypto", "volatility": 0.03},
    "BONUSD_otc": {"symbol_id": 416, "name": "Bonk (OTC)", "base_price": 0.000023, "group": "Crypto",
                   "volatility": 0.04},
    "MANUSD_otc": {"symbol_id": 417, "name": "Decentraland (OTC)", "base_price": 0.55, "group": "Crypto",
                   "volatility": 0.03},
    "MELUSD_otc": {"symbol_id": 418, "name": "Melania Meme (OTC)", "base_price": 1.85, "group": "Crypto",
                   "volatility": 0.035},
    "APTUSD_otc": {"symbol_id": 419, "name": "Aptos (OTC)", "base_price": 9.75, "group": "Crypto", "volatility": 0.028},
    "AVAUSD_otc": {"symbol_id": 420, "name": "Avalanche (OTC)", "base_price": 38.50, "group": "Crypto",
                   "volatility": 0.028},
    "BCHUSD_otc": {"symbol_id": 421, "name": "Bitcoin Cash (OTC)", "base_price": 425, "group": "Crypto",
                   "volatility": 0.025},
    "DOTUSD_otc": {"symbol_id": 422, "name": "Polkadot (OTC)", "base_price": 8.95, "group": "Crypto",
                   "volatility": 0.028},
    "LINUSD_otc": {"symbol_id": 423, "name": "Chainlink (OTC)", "base_price": 18.25, "group": "Crypto",
                   "volatility": 0.028},
    "ATOUSD_otc": {"symbol_id": 424, "name": "Cosmos (OTC)", "base_price": 11.50, "group": "Crypto",
                   "volatility": 0.028},
    "SOLUSD_otc": {"symbol_id": 425, "name": "Solana (OTC)", "base_price": 175, "group": "Crypto", "volatility": 0.026},
    "ADAUSD_otc": {"symbol_id": 426, "name": "Cardano (OTC)", "base_price": 0.58, "group": "Crypto",
                   "volatility": 0.03},
    "TONUSD_otc": {"symbol_id": 427, "name": "Toncoin (OTC)", "base_price": 6.85, "group": "Crypto",
                   "volatility": 0.028},
    "FLOUSD_otc": {"symbol_id": 428, "name": "Floki (OTC)", "base_price": 0.00023, "group": "Crypto",
                   "volatility": 0.04},
    "DASUSD_otc": {"symbol_id": 429, "name": "Dash (OTC)", "base_price": 32.50, "group": "Crypto", "volatility": 0.025},
    "BEAUSD_otc": {"symbol_id": 430, "name": "Beam (OTC)", "base_price": 0.022, "group": "Crypto", "volatility": 0.035},

    # ===== Stocks =====
    "MSFT_otc": {"symbol_id": 501, "name": "Microsoft (OTC)", "base_price": 420, "group": "Stocks",
                 "volatility": 0.015},
    "PFE_otc": {"symbol_id": 502, "name": "Pfizer (OTC)", "base_price": 28.50, "group": "Stocks", "volatility": 0.015},
    "BA_otc": {"symbol_id": 503, "name": "Boeing (OTC)", "base_price": 185, "group": "Stocks", "volatility": 0.018},
    "JNJ_otc": {"symbol_id": 504, "name": "Johnson & Johnson (OTC)", "base_price": 158, "group": "Stocks",
                "volatility": 0.012},
    "INTC_otc": {"symbol_id": 505, "name": "Intel (OTC)", "base_price": 42.50, "group": "Stocks", "volatility": 0.016},
    "MCD_otc": {"symbol_id": 506, "name": "McDonald's (OTC)", "base_price": 285, "group": "Stocks",
                "volatility": 0.012},
    "AXP_otc": {"symbol_id": 507, "name": "American Express (OTC)", "base_price": 225, "group": "Stocks",
                "volatility": 0.014},
    "FB_otc": {"symbol_id": 508, "name": "FACEBOOK INC (OTC)", "base_price": 485, "group": "Stocks",
               "volatility": 0.016},
}


def get_current_bd_time():
    """Returns current Bangladesh time (UTC+6) as datetime object"""
    return datetime.now(timezone(timedelta(hours=6)))


def format_price(price, asset_symbol):
    """Format price based on asset type"""
    asset_info = ASSETS.get(asset_symbol, {})

    # Crypto with very small prices
    if asset_symbol in ["SHIUSD_otc", "PEPUSD_otc", "BONUSD_otc", "FLOUSD_otc"]:
        return round(price, 8)
    # Other crypto
    elif asset_info.get("group") == "Crypto" and price < 0.01:
        return round(price, 6)
    elif asset_info.get("group") == "Crypto" and price < 1:
        return round(price, 4)
    # Commodities
    elif asset_symbol.startswith("XAU"):
        return round(price, 2)
    # Forex with high prices
    elif price > 1000:
        return round(price, 2)
    elif price > 100:
        return round(price, 3)
    elif price > 10:
        return round(price, 4)
    else:
        return round(price, 5)


def generate_candle_data(asset_symbol, target_time_bd):
    """Generate realistic candle data for a SPECIFIC Bangladesh time"""

    # Get asset info
    if asset_symbol not in ASSETS:
        # Default to BRLUSD_otc if not found
        asset_info = ASSETS["BRLUSD_otc"]
    else:
        asset_info = ASSETS[asset_symbol]

    base_price = asset_info["base_price"]
    volatility = asset_info.get("volatility", 0.002)

    # Use the target time for this candle
    candle_time_bd = target_time_bd

    # Convert to Unix timestamp
    candle_unix_time = int(candle_time_bd.timestamp())

    # Add randomness based on the minute
    minute_seed = candle_time_bd.minute + (candle_time_bd.hour * 60)
    random.seed(minute_seed + asset_info["symbol_id"])  # Unique per asset

    # Create small trend
    hour_factor = (candle_time_bd.hour - 12) / 1000

    change = random.uniform(-volatility, volatility) + hour_factor

    # Calculate OHLC prices
    open_price = base_price * (1 + (minute_seed * 0.00005))
    close_price = open_price * (1 + change)
    high_price = max(open_price, close_price) * (1 + random.uniform(0, volatility / 3))
    low_price = min(open_price, close_price) * (1 - random.uniform(0, volatility / 3))

    # Reset random seed
    random.seed()

    # Format the readable time string
    time_read = candle_time_bd.strftime("%Y-%m-%d %H:%M (UTC: +06:00)")

    # Create candle
    candle = {
        "symbol_id": asset_info["symbol_id"],
        "time": candle_unix_time,
        "open": format_price(open_price, asset_symbol),
        "close": format_price(close_price, asset_symbol),
        "high": format_price(high_price, asset_symbol),
        "low": format_price(low_price, asset_symbol),
        "ticks": random.randint(50, 200),
        "last_tick": time.time(),
        "asset": asset_symbol,
        "asset_name": asset_info["name"],
        "time_read": time_read
    }

    return candle


@app.route('/quotex_candles', methods=['GET'])
def get_candles():
    """Main API endpoint - Get candle data (default: 10 candles)"""
    asset = request.args.get('assets', 'BRLUSD_otc')
    limit = request.args.get('limit', 10, type=int)

    try:
        if asset not in ASSETS:
            return jsonify({"error": f"Asset '{asset}' not found. Use /assets to see all 100+ pairs."}), 404

        bd_now = get_current_bd_time()

        candles = []
        for i in range(limit):
            candle_time = bd_now - timedelta(minutes=i)
            candle = generate_candle_data(asset, candle_time)
            candles.append(candle)

        # Return in chronological order (oldest first)
        return jsonify(list(reversed(candles)))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/assets', methods=['GET'])
def list_assets():
    """List all available assets with grouping"""
    assets_by_group = {}

    for symbol, info in ASSETS.items():
        group = info.get("group", "Other")
        if group not in assets_by_group:
            assets_by_group[group] = []

        assets_by_group[group].append({
            "symbol_id": info["symbol_id"],
            "asset": symbol,
            "asset_name": info["name"],
            "base_price": info["base_price"]
        })

    # Sort assets within each group by symbol_id
    for group in assets_by_group:
        assets_by_group[group].sort(key=lambda x: x["symbol_id"])

    return jsonify({
        "total_assets": len(ASSETS),
        "groups": assets_by_group
    })


@app.route('/assets/simple', methods=['GET'])
def list_assets_simple():
    """Simple list of all assets (for dropdown menus)"""
    assets_list = []
    for symbol, info in ASSETS.items():
        assets_list.append({
            "value": symbol,
            "label": info["name"],
            "group": info.get("group", "Other")
        })

    # Sort by group then symbol
    assets_list.sort(key=lambda x: (x["group"], x["value"]))

    return jsonify(assets_list)


@app.route('/')
def home():
    """Homepage with API documentation"""
    bd_now = get_current_bd_time()

    # Count assets by group
    groups = {}
    for info in ASSETS.values():
        group = info.get("group", "Other")
        groups[group] = groups.get(group, 0) + 1

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>JummooBot Trading API - 100+ Pairs</title>
        <style>
            body {{ font-family: Arial; max-width: 1200px; margin: 50px auto; padding: 20px; background: #f5f5f5; }}
            h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
            h2 {{ color: #34495e; margin-top: 30px; }}
            .current-time {{ background: #2c3e50; color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
            .stats {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 20px 0; }}
            .stat-card {{ background: white; padding: 15px; border-radius: 8px; flex: 1; min-width: 150px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .stat-number {{ font-size: 24px; font-weight: bold; color: #3498db; }}
            .endpoint {{ background: white; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .group-badge {{ background: #3498db; color: white; padding: 3px 10px; border-radius: 15px; font-size: 12px; display: inline-block; margin: 2px; }}
            code {{ background: #ecf0f1; padding: 3px 8px; border-radius: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #3498db; color: white; }}
            tr:hover {{ background: #f5f5f5; }}
        </style>
    </head>
    <body>
        <h1>🚀 JummooBot Trading API</h1>

        <div class="current-time">
            🇧🇩 Bangladesh Time: <strong>{bd_now.strftime("%Y-%m-%d %H:%M:%S")}</strong>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(ASSETS)}</div>
                <div>Total Trading Pairs</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{groups.get('Forex Real', 0)}</div>
                <div>Forex Real</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{groups.get('Forex OTC', 0)}</div>
                <div>Forex OTC</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{groups.get('Crypto', 0)}</div>
                <div>Cryptocurrencies</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{groups.get('Commodities Real', 0) + groups.get('Commodities OTC', 0)}</div>
                <div>Commodities</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{groups.get('Stocks', 0)}</div>
                <div>Stocks</div>
            </div>
        </div>

        <div class="endpoint">
            <h3>📡 DEFAULT (10 candles):</h3>
            <code>GET /quotex_candles?assets=BRLUSD_otc</code><br>
            <a href="/quotex_candles?assets=BRLUSD_otc" target="_blank">Try it: BRLUSD_otc (10 candles)</a>
        </div>

        <div class="endpoint">
            <h3>📡 Single Candle:</h3>
            <code>GET /quotex_candles?assets=BRLUSD_otc&limit=1</code><br>
            <a href="/quotex_candles?assets=BRLUSD_otc&limit=1" target="_blank">Try it: Single candle</a>
        </div>

        <div class="endpoint">
            <h3>📋 All Assets (grouped):</h3>
            <code>GET /assets</code><br>
            <a href="/assets" target="_blank">View all 100+ pairs with groups</a>
        </div>

        <div class="endpoint">
            <h3>📋 Simple Asset List (for dropdowns):</h3>
            <code>GET /assets/simple</code><br>
            <a href="/assets/simple" target="_blank">View simple list</a>
        </div>

        <h2>🔥 Popular Pairs:</h2>
        <div style="display: flex; flex-wrap: wrap; gap: 10px;">
            <a href="/quotex_candles?assets=EURUSD" class="group-badge">EURUSD</a>
            <a href="/quotex_candles?assets=GBPUSD" class="group-badge">GBPUSD</a>
            <a href="/quotex_candles?assets=USDJPY" class="group-badge">USDJPY</a>
            <a href="/quotex_candles?assets=EURUSD_otc" class="group-badge">EURUSD_otc</a>
            <a href="/quotex_candles?assets=GBPUSD_otc" class="group-badge">GBPUSD_otc</a>
            <a href="/quotex_candles?assets=BRLUSD_otc" class="group-badge">BRLUSD_otc</a>
            <a href="/quotex_candles?assets=USDBDT_otc" class="group-badge">USDBDT_otc</a>
            <a href="/quotex_candles?assets=USDINR_otc" class="group-badge">USDINR_otc</a>
            <a href="/quotex_candles?assets=XAUUSD" class="group-badge">XAUUSD</a>
            <a href="/quotex_candles?assets=BTCUSD_otc" class="group-badge">BTCUSD_otc</a>
            <a href="/quotex_candles?assets=ETHUSD_otc" class="group-badge">ETHUSD_otc</a>
            <a href="/quotex_candles?assets=MSFT_otc" class="group-badge">MSFT_otc</a>
        </div>

        <h2>📊 Sample Response:</h2>
        <pre>{{
  "symbol_id": 332,
  "time": {int(time.time()) + 6 * 3600},
  "open": 0.1896,
  "close": 0.18945,
  "high": 0.18966,
  "low": 0.18945,
  "ticks": 81,
  "last_tick": {time.time()},
  "asset": "BRLUSD_otc",
  "asset_name": "USD/BRL (OTC)",
  "time_read": "{bd_now.strftime('%Y-%m-%d %H:%M (UTC: +06:00)')}"
}}</pre>

        <p>✅ <strong>Total: {len(ASSETS)} trading pairs available!</strong></p>
    </body>
    </html>
    """


@app.route('/health')
def health():
    """Health check endpoint"""
    bd_now = get_current_bd_time()
    return jsonify({
        "status": "healthy",
        "bangladesh_time": bd_now.isoformat(),
        "timezone": "UTC+6",
        "version": "6.0.0",
        "total_assets": len(ASSETS),
        "default_candles": 10
    })


if __name__ == '__main__':
    current_bd = get_current_bd_time()
    print("=" * 70)
    print("🚀 JummooBot Trading API - MEGA EDITION")
    print("=" * 70)
    print(f"🇧🇩 Bangladesh Time: {current_bd.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📍 Local URL: http://localhost:5000")
    print(f"📊 TOTAL ASSETS: {len(ASSETS)} trading pairs")
    print("-" * 70)

    # Count by group
    groups = {}
    for info in ASSETS.values():
        group = info.get("group", "Other")
        groups[group] = groups.get(group, 0) + 1

    for group, count in groups.items():
        print(f"   {group}: {count} pairs")

    print("-" * 70)
    print("🔥 Try: http://localhost:5000/quotex_candles?assets=BRLUSD_otc")
    print("📋 All assets: http://localhost:5000/assets")
    print("=" * 70)

    app.run(debug=True, host='0.0.0.0', port=5000)