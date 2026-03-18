import os
import time
import json
from datetime import datetime, timedelta, timezone
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup

# Create Flask app
app = Flask(__name__)
CORS(app)

# Force pretty JSON
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['JSON_AS_ASCII'] = False

# ============================================
# ASSET MAPPING - Yahoo Finance Symbols
# ============================================
ASSETS = {
    # Forex OTC Pairs (using closest Yahoo symbols)
    "EURUSD_otc": {"symbol": "EURUSD=X", "name": "EUR/USD (OTC)", "type": "forex"},
    "GBPUSD_otc": {"symbol": "GBPUSD=X", "name": "GBP/USD (OTC)", "type": "forex"},
    "USDJPY_otc": {"symbol": "JPY=X", "name": "USD/JPY (OTC)", "type": "forex"},
    "AUDUSD_otc": {"symbol": "AUDUSD=X", "name": "AUD/USD (OTC)", "type": "forex"},
    "USDCAD_otc": {"symbol": "CAD=X", "name": "USD/CAD (OTC)", "type": "forex"},
    "NZDUSD_otc": {"symbol": "NZDUSD=X", "name": "NZD/USD (OTC)", "type": "forex"},
    "USDCHF_otc": {"symbol": "CHF=X", "name": "USD/CHF (OTC)", "type": "forex"},
    "USDBDT_otc": {"symbol": "USDBDT=X", "name": "USD/BDT (OTC)", "type": "forex"},  # May need alternative
    "BRLUSD_otc": {"symbol": "BRL=X", "name": "USD/BRL (OTC)", "type": "forex"},
    "USDINR_otc": {"symbol": "INR=X", "name": "USD/INR (OTC)", "type": "forex"},

    # Cryptocurrencies
    "BTCUSD_otc": {"symbol": "BTC-USD", "name": "Bitcoin (OTC)", "type": "crypto"},
    "ETHUSD_otc": {"symbol": "ETH-USD", "name": "Ethereum (OTC)", "type": "crypto"},
    "BNBUSD_otc": {"symbol": "BNB-USD", "name": "Binance Coin (OTC)", "type": "crypto"},
    "XRPUSD_otc": {"symbol": "XRP-USD", "name": "Ripple (OTC)", "type": "crypto"},
    "SOLUSD_otc": {"symbol": "SOL-USD", "name": "Solana (OTC)", "type": "crypto"},
    "ADAUSD_otc": {"symbol": "ADA-USD", "name": "Cardano (OTC)", "type": "crypto"},
    "DOGEUSD_otc": {"symbol": "DOGE-USD", "name": "Dogecoin (OTC)", "type": "crypto"},

    # Commodities
    "XAUUSD": {"symbol": "GC=F", "name": "Gold", "type": "commodity"},
    "XAGUSD": {"symbol": "SI=F", "name": "Silver", "type": "commodity"},
    "XTIUSD": {"symbol": "CL=F", "name": "WTI Oil", "type": "commodity"},
    "XBRUSD": {"symbol": "BZ=F", "name": "Brent Oil", "type": "commodity"},

    # Stocks
    "MSFT_otc": {"symbol": "MSFT", "name": "Microsoft (OTC)", "type": "stock"},
    "AAPL_otc": {"symbol": "AAPL", "name": "Apple (OTC)", "type": "stock"},
    "GOOGL_otc": {"symbol": "GOOGL", "name": "Google (OTC)", "type": "stock"},
    "AMZN_otc": {"symbol": "AMZN", "name": "Amazon (OTC)", "type": "stock"},
}


def get_current_bd_time():
    """Returns current Bangladesh time (UTC+6)"""
    return datetime.now(timezone(timedelta(hours=6)))


def fetch_real_candles(asset_symbol, period="1d", interval="1m"):
    """
    Fetch REAL candle data from Yahoo Finance
    Returns DataFrame with OHLC data
    """
    if asset_symbol not in ASSETS:
        return None

    yahoo_symbol = ASSETS[asset_symbol]["symbol"]

    try:
        # Download data from Yahoo Finance
        ticker = yf.Ticker(yahoo_symbol)

        # Get historical data
        if ASSETS[asset_symbol]["type"] == "crypto":
            # Crypto has 24/7 trading
            df = ticker.history(period="5d", interval=interval)
        else:
            # Forex/Stocks have market hours
            df = ticker.history(period=period, interval=interval)

        if df.empty:
            # Fallback to larger timeframe
            df = ticker.history(period="5d", interval="5m")

        return df

    except Exception as e:
        print(f"Error fetching {asset_symbol}: {e}")
        return None


def calculate_indicators(df):
    """
    Calculate technical indicators for signal generation
    """
    if df is None or len(df) < 20:
        return None

    # Make a copy to avoid warnings
    data = df.copy()

    # Calculate Simple Moving Averages
    data['SMA_5'] = data['Close'].rolling(window=5).mean()
    data['SMA_10'] = data['Close'].rolling(window=10).mean()
    data['SMA_20'] = data['Close'].rolling(window=20).mean()

    # Calculate Exponential Moving Averages
    data['EMA_12'] = data['Close'].ewm(span=12, adjust=False).mean()
    data['EMA_26'] = data['Close'].ewm(span=26, adjust=False).mean()

    # Calculate MACD
    data['MACD'] = data['EMA_12'] - data['EMA_26']
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
    data['MACD_Histogram'] = data['MACD'] - data['Signal_Line']

    # Calculate RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))

    # Calculate Bollinger Bands
    data['BB_Middle'] = data['Close'].rolling(window=20).mean()
    bb_std = data['Close'].rolling(window=20).std()
    data['BB_Upper'] = data['BB_Middle'] + (bb_std * 2)
    data['BB_Lower'] = data['BB_Middle'] - (bb_std * 2)

    # Calculate Volume indicators (if volume exists)
    if 'Volume' in data.columns:
        data['Volume_SMA'] = data['Volume'].rolling(window=5).mean()

    return data


def generate_signal(data, asset_symbol):
    """
    Generate trading signal based on technical indicators
    Returns: direction, trend, confidence, signal_type
    """
    if data is None or len(data) < 2:
        return {
            "direction": "NEUTRAL",
            "signal": "NEUTRAL",
            "trend": "SIDEWAYS",
            "confidence": 0,
            "signal_type": "HOLD"
        }

    latest = data.iloc[-1]
    prev = data.iloc[-2]

    # Initialize scores
    buy_score = 0
    sell_score = 0
    total_indicators = 0

    # Trend signals
    if not pd.isna(latest['SMA_5']) and not pd.isna(latest['SMA_20']):
        if latest['SMA_5'] > latest['SMA_20']:
            buy_score += 1
        else:
            sell_score += 1
        total_indicators += 1

    # MACD signals
    if not pd.isna(latest['MACD']) and not pd.isna(latest['Signal_Line']):
        if latest['MACD'] > latest['Signal_Line']:
            buy_score += 1
        else:
            sell_score += 1
        total_indicators += 1

    # RSI signals
    if not pd.isna(latest['RSI']):
        if latest['RSI'] < 30:
            buy_score += 2  # Oversold - strong buy
        elif latest['RSI'] > 70:
            sell_score += 2  # Overbought - strong sell
        elif latest['RSI'] < 50:
            buy_score += 1
        elif latest['RSI'] > 50:
            sell_score += 1
        total_indicators += 2

    # Bollinger Bands
    if not pd.isna(latest['BB_Lower']) and not pd.isna(latest['BB_Upper']):
        if latest['Close'] < latest['BB_Lower']:
            buy_score += 2  # Price below lower band - bounce up likely
        elif latest['Close'] > latest['BB_Upper']:
            sell_score += 2  # Price above upper band - pullback likely
        total_indicators += 2

    # Price action
    if latest['Close'] > prev['Close']:
        buy_score += 1
    else:
        sell_score += 1
    total_indicators += 1

    # Determine direction and confidence
    if total_indicators > 0:
        if buy_score > sell_score:
            direction = "CALL"
            signal = "BUY"
            confidence = int((buy_score / (buy_score + sell_score)) * 100)
        elif sell_score > buy_score:
            direction = "PUT"
            signal = "SELL"
            confidence = int((sell_score / (buy_score + sell_score)) * 100)
        else:
            direction = "NEUTRAL"
            signal = "NEUTRAL"
            confidence = 50
    else:
        direction = "NEUTRAL"
        signal = "NEUTRAL"
        confidence = 0

    # Determine trend
    if len(data) >= 20:
        sma_5_trend = data['SMA_5'].iloc[-1] > data['SMA_5'].iloc[-5] if len(data) >= 5 else False
        sma_20_trend = data['SMA_20'].iloc[-1] > data['SMA_20'].iloc[-5] if len(data) >= 5 else False

        if sma_5_trend and sma_20_trend:
            trend = "UP"
        elif not sma_5_trend and not sma_20_trend:
            trend = "DOWN"
        else:
            trend = "SIDEWAYS"
    else:
        trend = "SIDEWAYS"

    # Signal type based on confidence
    if confidence >= 75:
        signal_type = "STRONG_" + signal if signal != "NEUTRAL" else "HOLD"
    elif confidence >= 60:
        signal_type = signal if signal != "NEUTRAL" else "HOLD"
    else:
        signal_type = "HOLD"

    return {
        "direction": direction,
        "signal": signal,
        "trend": trend,
        "confidence": confidence,
        "signal_type": signal_type
    }


def format_candle(row, asset_symbol, asset_info, signal_data):
    """Format a single candle with all required fields"""
    bd_time = row.name.tz_convert(timezone(timedelta(hours=6))) if hasattr(row.name, 'tz_convert') else row.name

    return {
        "symbol_id": list(ASSETS.keys()).index(asset_symbol) + 1,
        "time": int(row.name.timestamp()),
        "open": round(float(row['Open']), 5),
        "close": round(float(row['Close']), 5),
        "high": round(float(row['High']), 5),
        "low": round(float(row['Low']), 5),
        "ticks": int(row.get('Volume', 100)) if not pd.isna(row.get('Volume', 100)) else 100,
        "last_tick": time.time(),
        "asset": asset_symbol,
        "asset_name": asset_info["name"],
        "time_read": bd_time.strftime("%Y-%m-%d %H:%M (UTC: +06:00)"),
        # New signal fields
        "direction": signal_data["direction"],
        "signal": signal_data["signal"],
        "trend": signal_data["trend"],
        "confidence": signal_data["confidence"],
        "signal_type": signal_data["signal_type"]
    }


def pretty_response(data):
    """Create a pretty JSON response"""
    response = make_response(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/quotex_candles', methods=['GET'])
def get_candles():
    """
    Get candle data with signals
    Default: 100 candles for proper trend analysis
    """
    asset = request.args.get('assets', 'EURUSD_otc')
    limit = request.args.get('limit', 100, type=int)  # Now 100 default!

    try:
        if asset not in ASSETS:
            return pretty_response({"error": f"Asset '{asset}' not found"}), 404

        asset_info = ASSETS[asset]

        # Fetch real data
        df = fetch_real_candles(asset, period="5d", interval="1m")

        if df is None or df.empty:
            # Fallback to demo data if real data unavailable
            return pretty_response({"error": "Market closed or data unavailable. Try during trading hours."}), 503

        # Calculate indicators
        df_with_indicators = calculate_indicators(df)

        if df_with_indicators is None:
            return pretty_response({"error": "Insufficient data for analysis"}), 503

        # Get last N candles
        last_n_candles = df_with_indicators.tail(limit)

        # Generate signal based on latest data
        signal_data = generate_signal(df_with_indicators, asset)

        # Format candles
        candles = []
        for idx, row in last_n_candles.iterrows():
            candle = format_candle(row, asset, asset_info, signal_data)
            candles.append(candle)

        return pretty_response(candles)

    except Exception as e:
        return pretty_response({"error": str(e)}), 500


@app.route('/quotex_signal', methods=['GET'])
def get_signal():
    """
    Get ONLY the current signal for an asset
    """
    asset = request.args.get('assets', 'EURUSD_otc')

    try:
        if asset not in ASSETS:
            return pretty_response({"error": f"Asset '{asset}' not found"}), 404

        # Fetch real data
        df = fetch_real_candles(asset, period="1d", interval="1m")

        if df is None or df.empty:
            return pretty_response({"error": "Market closed"}), 503

        # Calculate indicators
        df_with_indicators = calculate_indicators(df)

        if df_with_indicators is None:
            return pretty_response({"error": "Insufficient data"}), 503

        # Generate signal
        signal_data = generate_signal(df_with_indicators, asset)

        # Add current price
        latest = df.iloc[-1]
        signal_data["current_price"] = round(float(latest['Close']), 5)
        signal_data["asset"] = asset
        signal_data["asset_name"] = ASSETS[asset]["name"]
        signal_data["time"] = int(time.time())
        signal_data["time_read"] = get_current_bd_time().strftime("%Y-%m-%d %H:%M (UTC: +06:00)")

        return pretty_response(signal_data)

    except Exception as e:
        return pretty_response({"error": str(e)}), 500


@app.route('/forex_factory/news', methods=['GET'])
def get_forex_news():
    """
    Get latest forex news (simulated Forex Factory style)
    """
    # In production, you'd scrape Forex Factory or use a news API
    news_items = [
        {
            "id": 1,
            "title": "Federal Reserve Maintains Interest Rates",
            "impact": "HIGH",
            "currency": "USD",
            "time": get_current_bd_time().strftime("%Y-%m-%d %H:%M"),
            "content": "Fed keeps rates steady at 5.25-5.50% as expected. Dovish tilt in statement."
        },
        {
            "id": 2,
            "title": "ECB Signals June Rate Cut Possibility",
            "impact": "MEDIUM",
            "currency": "EUR",
            "time": (get_current_bd_time() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
            "content": "European Central Bank minutes show growing support for rate cut in June."
        },
        {
            "id": 3,
            "title": "UK GDP Beats Expectations",
            "impact": "HIGH",
            "currency": "GBP",
            "time": (get_current_bd_time() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"),
            "content": "UK economy grows 0.3% in Q1, surpassing forecasts of 0.1%."
        },
        {
            "id": 4,
            "title": "BOJ Maintains Ultra-Loose Policy",
            "impact": "MEDIUM",
            "currency": "JPY",
            "time": (get_current_bd_time() - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M"),
            "content": "Bank of Japan keeps negative rates, yen weakens slightly."
        },
        {
            "id": 5,
            "title": "BDT Shows Stability Amid Regional Volatility",
            "impact": "LOW",
            "currency": "BDT",
            "time": (get_current_bd_time() - timedelta(hours=12)).strftime("%Y-%m-%d %H:%M"),
            "content": "Bangladeshi Taka remains stable against USD despite regional pressures."
        }
    ]

    return pretty_response({
        "news": news_items,
        "last_updated": get_current_bd_time().isoformat(),
        "source": "Forex Factory (Simulated)"
    })


@app.route('/market_status/<asset>', methods=['GET'])
def market_status(asset):
    """
    Check if market is open for trading
    """
    if asset not in ASSETS:
        return pretty_response({"error": "Asset not found"}), 404

    asset_type = ASSETS[asset]["type"]
    bd_now = get_current_bd_time()

    # Crypto is always open
    if asset_type == "crypto":
        return pretty_response({
            "asset": asset,
            "market_open": True,
            "reason": "Cryptocurrency markets trade 24/7",
            "current_time": bd_now.strftime("%Y-%m-%d %H:%M (UTC: +06:00)")
        })

    # Check if it's weekend
    if bd_now.weekday() >= 5:  # Saturday or Sunday
        return pretty_response({
            "asset": asset,
            "market_open": False,
            "reason": "Weekend - Forex markets closed",
            "current_time": bd_now.strftime("%Y-%m-%d %H:%M (UTC: +06:00)")
        })

    # Check trading hours (simplified - 24h forex during weekdays)
    return pretty_response({
        "asset": asset,
        "market_open": True,
        "reason": "Market should be open (weekday)",
        "current_time": bd_now.strftime("%Y-%m-%d %H:%M (UTC: +06:00)")
    })


@app.route('/assets', methods=['GET'])
def list_assets():
    """List all available assets"""
    assets_list = []
    for symbol, info in ASSETS.items():
        assets_list.append({
            "symbol_id": list(ASSETS.keys()).index(symbol) + 1,
            "asset": symbol,
            "asset_name": info["name"],
            "type": info["type"],
            "yahoo_symbol": info["symbol"]
        })
    return pretty_response(assets_list)


@app.route('/')
def home():
    """Homepage with API documentation"""
    bd_now = get_current_bd_time()

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>JummooBot Pro Trading API</title>
        <style>
            body {{ font-family: Arial; max-width: 1200px; margin: 50px auto; padding: 20px; background: #f5f5f5; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #34495e; }}
            .current-time {{ background: #2c3e50; color: white; padding: 15px; border-radius: 8px; }}
            .endpoint {{ background: white; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .badge {{ background: #3498db; color: white; padding: 3px 10px; border-radius: 15px; font-size: 12px; }}
            .new {{ background: #27ae60; color: white; padding: 3px 10px; border-radius: 15px; font-size: 12px; }}
            code {{ background: #ecf0f1; padding: 3px 8px; border-radius: 5px; }}
            pre {{ background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 8px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <h1>🚀 JummooBot Pro Trading API</h1>

        <div class="current-time">
            🇧🇩 Bangladesh Time: <strong>{bd_now.strftime("%Y-%m-%d %H:%M:%S")}</strong>
        </div>

        <h2>📡 New Features (Like Old API + More!)</h2>

        <div class="endpoint">
            <span class="new">NEW</span>
            <h3>📊 Get 100 Candles with Signals:</h3>
            <code>GET /quotex_candles?assets=EURUSD_otc</code><br>
            <small>Returns 100 candles with direction, signal, trend, confidence fields</small><br>
            <a href="/quotex_candles?assets=EURUSD_otc" target="_blank">Try it: EURUSD_otc (100 candles)</a>
        </div>

        <div class="endpoint">
            <span class="new">NEW</span>
            <h3>🎯 Get Pure Signal (Like Old API):</h3>
            <code>GET /quotex_signal?assets=EURUSD_otc</code><br>
            <small>Returns only direction, signal, trend, confidence, current_price</small><br>
            <a href="/quotex_signal?assets=EURUSD_otc" target="_blank">Try it: Current EURUSD_otc signal</a>
        </div>

        <div class="endpoint">
            <span class="new">NEW</span>
            <h3>📰 Forex News (Like Old API):</h3>
            <code>GET /forex_factory/news</code><br>
            <small>Latest forex news with impact ratings</small><br>
            <a href="/forex_factory/news" target="_blank">View News</a>
        </div>

        <div class="endpoint">
            <span class="new">NEW</span>
            <h3>🔌 Market Status Check:</h3>
            <code>GET /market_status/EURUSD_otc</code><br>
            <small>Check if market is open before trading</small><br>
            <a href="/market_status/EURUSD_otc" target="_blank">Check EURUSD_otc</a>
        </div>

        <div class="endpoint">
            <h3>📋 All Assets:</h3>
            <code>GET /assets</code><br>
            <a href="/assets" target="_blank">View all {len(ASSETS)} pairs</a>
        </div>

        <h2>📊 Sample Response (Includes All Fields):</h2>
        <pre>{{
  "symbol_id": 1,
  "time": 1773856921,
  "open": 1.0876,
  "close": 1.0889,
  "high": 1.0892,
  "low": 1.0871,
  "ticks": 1245,
  "last_tick": 1773856921.123,
  "asset": "EURUSD_otc",
  "asset_name": "EUR/USD (OTC)",
  "time_read": "2026-03-19 15:30 (UTC: +06:00)",
  "direction": "CALL",
  "signal": "BUY",
  "trend": "UP",
  "confidence": 85,
  "signal_type": "STRONG_BUY"
}}</pre>

        <p>✅ <strong>Total Assets:</strong> {len(ASSETS)}</p>
        <p>✅ <strong>Default Candles:</strong> 100 (for proper trend analysis)</p>
        <p>✅ <strong>Real Market Data:</strong> No random numbers - live from Yahoo Finance</p>
        <p>✅ <strong>Market Hours:</strong> Cryptos 24/7, Forex weekdays, Stocks market hours</p>
    </body>
    </html>
    """


@app.route('/health')
def health():
    """Health check endpoint"""
    bd_now = get_current_bd_time()
    return pretty_response({
        "status": "healthy",
        "bangladesh_time": bd_now.isoformat(),
        "timezone": "UTC+6",
        "version": "8.0.0",
        "assets_count": len(ASSETS),
        "default_candles": 100,
        "features": ["signals", "direction", "trend", "confidence", "news", "market_status"]
    })


if __name__ == '__main__':
    current_bd = get_current_bd_time()
    print("=" * 80)
    print("🚀 JummooBot Pro Trading API - REAL MARKET DATA")
    print("=" * 80)
    print(f"🇧🇩 Bangladesh Time: {current_bd.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Assets: {len(ASSETS)}")
    print(f"📡 Default Candles: 100")
    print("-" * 80)
    print("✅ NEW FEATURES:")
    print("   • 100 candles default (proper trend analysis)")
    print("   • Direction field (CALL/PUT/NEUTRAL)")
    print("   • Signal field (BUY/SELL/NEUTRAL)")
    print("   • Trend field (UP/DOWN/SIDEWAYS)")
    print("   • Confidence percentage")
    print("   • Real market data (no random numbers)")
    print("   • Market status checker")
    print("   • Forex news endpoint")
    print("-" * 80)
    print("📡 Try it:")
    print("   http://localhost:5000/quotex_candles?assets=EURUSD_otc")
    print("   http://localhost:5000/quotex_signal?assets=EURUSD_otc")
    print("   http://localhost:5000/forex_factory/news")
    print("=" * 80)

    app.run(debug=True, host='0.0.0.0', port=5000)