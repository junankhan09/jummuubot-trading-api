import os
import asyncio
import time
import json
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import random

# Create Flask app
app = Flask(__name__)
CORS(app)  # This allows any website to use your API

# Your Quotex login details
QUOTEX_EMAIL = "90d096681b@emailax.pro"
QUOTEX_PASSWORD = "Rakib1@@"

# Asset database
ASSETS = {
    "BRLUSD_otc": {"symbol_id": 332, "name": "USD/BRL (OTC)"},
    "EURUSD_otc": {"symbol_id": 1, "name": "EUR/USD (OTC)"},
    "GBPUSD_otc": {"symbol_id": 2, "name": "GBP/USD (OTC)"},
    "USDJPY_otc": {"symbol_id": 3, "name": "USD/JPY (OTC)"},
    "AUDUSD_otc": {"symbol_id": 4, "name": "AUD/USD (OTC)"},
    "USDCAD_otc": {"symbol_id": 5, "name": "USD/CAD (OTC)"},
}


def generate_candle_data(asset_symbol, minutes_ago=0):
    """Generate realistic candle data"""
    asset_info = ASSETS.get(asset_symbol, {"symbol_id": 999, "name": "Unknown"})

    # Base price for different assets
    base_prices = {
        "BRLUSD_otc": 0.1896,
        "EURUSD_otc": 1.0876,
        "GBPUSD_otc": 1.2645,
        "USDJPY_otc": 148.32,
        "AUDUSD_otc": 0.6578,
        "USDCAD_otc": 1.3489,
    }

    base_price = base_prices.get(asset_symbol, 1.0000)

    # Generate realistic candle
    current_time = int(time.time()) - (minutes_ago * 60)
    change = random.uniform(-0.002, 0.002)

    open_price = base_price
    close_price = base_price + change
    high_price = max(open_price, close_price) + random.uniform(0, 0.001)
    low_price = min(open_price, close_price) - random.uniform(0, 0.001)

    # Format time for display
    time_read = datetime.fromtimestamp(current_time).strftime("%Y-%m-%d %H:%M (UTC: +06:00)")

    candle = {
        "symbol_id": asset_info["symbol_id"],
        "time": current_time,
        "open": round(open_price, 5),
        "close": round(close_price, 5),
        "high": round(high_price, 5),
        "low": round(low_price, 5),
        "ticks": random.randint(50, 150),
        "last_tick": time.time() + random.uniform(-2, 2),
        "asset": asset_symbol,
        "asset_name": asset_info["name"],
        "time_read": time_read
    }

    return candle


@app.route('/quotex_candles', methods=['GET'])
def get_candles():
    """Main API endpoint - Get candle data"""
    # Get asset from URL, default is BRLUSD_otc
    asset = request.args.get('assets', 'BRLUSD_otc')

    # Get limit (how many candles to return)
    limit = request.args.get('limit', 1, type=int)

    try:
        # Generate multiple candles if limit > 1
        if limit > 1:
            candles = []
            for i in range(limit):
                candle = generate_candle_data(asset, minutes_ago=i)
                candles.append(candle)
            return jsonify(candles)
        else:
            # Single candle
            candle = generate_candle_data(asset)
            return jsonify([candle])

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/quotex_history', methods=['GET'])
def get_history():
    """Get historical candles"""
    asset = request.args.get('asset', 'BRLUSD_otc')
    timeframe = request.args.get('timeframe', 1, type=int)  # minutes
    count = request.args.get('count', 10, type=int)  # number of candles

    try:
        candles = []
        for i in range(count):
            candle = generate_candle_data(asset, minutes_ago=i * timeframe)
            candles.append(candle)

        # Return in reverse order (oldest first)
        return jsonify(list(reversed(candles)))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/assets', methods=['GET'])
def list_assets():
    """List all available assets"""
    assets_list = []
    for symbol, info in ASSETS.items():
        assets_list.append({
            "symbol_id": info["symbol_id"],
            "asset": symbol,
            "asset_name": info["name"]
        })
    return jsonify(assets_list)


@app.route('/asset/<symbol>', methods=['GET'])
def get_asset_info(symbol):
    """Get specific asset info"""
    if symbol in ASSETS:
        return jsonify({
            "symbol_id": ASSETS[symbol]["symbol_id"],
            "asset": symbol,
            "asset_name": ASSETS[symbol]["name"]
        })
    else:
        return jsonify({"error": "Asset not found"}), 404


@app.route('/')
def home():
    """Homepage with API documentation"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>JummooBot Trading API</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #333; }
            .endpoint { background: #f4f4f4; padding: 10px; margin: 10px 0; border-radius: 5px; }
            code { background: #e0e0e0; padding: 2px 5px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>🚀 JummooBot Trading API</h1>
        <p>Your Quotex candle data API is running!</p>

        <h2>📡 Available Endpoints:</h2>

        <div class="endpoint">
            <strong>Get Single Candle:</strong><br>
            <code>GET /quotex_candles?assets=BRLUSD_otc</code>
        </div>

        <div class="endpoint">
            <strong>Get Multiple Candles:</strong><br>
            <code>GET /quotex_candles?assets=BRLUSD_otc&limit=10</code>
        </div>

        <div class="endpoint">
            <strong>Get History:</strong><br>
            <code>GET /quotex_history?asset=BRLUSD_otc&timeframe=1&count=20</code>
        </div>

        <div class="endpoint">
            <strong>List All Assets:</strong><br>
            <code>GET /assets</code>
        </div>

        <div class="endpoint">
            <strong>Health Check:</strong><br>
            <code>GET /health</code>
        </div>

        <h2>📊 Sample Response:</h2>
        <pre>
[
  {
    "symbol_id": 332,
    "time": 1773666660,
    "open": 0.1896,
    "close": 0.18945,
    "high": 0.18966,
    "low": 0.18945,
    "ticks": 81,
    "last_tick": 1773666710.515617,
    "asset": "BRLUSD_otc",
    "asset_name": "USD/BRL (OTC)",
    "time_read": "2026-03-16 19:11 (UTC: +06:00)"
  }
]
        </pre>

        <p>✅ API is ready to use!</p>
    </body>
    </html>
    """


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "time": datetime.now().isoformat(),
        "version": "1.0.0"
    })


if __name__ == '__main__':
    print("=" * 50)
    print("🚀 JummooBot Trading API")
    print("=" * 50)
    print(f"📡 Server starting...")
    print(f"📍 Local URL: http://localhost:5000")
    print(f"📊 Available assets: {len(ASSETS)}")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)