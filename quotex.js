/ quotex.js - Complete Trading API for Cloudflare Workers
// JavaScript version of your Flask API

// ==================== ASSET DATABASE ====================
const ASSETS = {
    // Forex Real Market
    "EURUSD": { symbol_id: 101, name: "EUR/USD", base_price: 1.0876, group: "Forex Real", volatility: 0.002 },
    "GBPUSD": { symbol_id: 102, name: "GBP/USD", base_price: 1.2645, group: "Forex Real", volatility: 0.002 },
    "USDJPY": { symbol_id: 103, name: "USD/JPY", base_price: 148.32, group: "Forex Real", volatility: 0.003 },
    "USDCHF": { symbol_id: 104, name: "USD/CHF", base_price: 0.8765, group: "Forex Real", volatility: 0.002 },
    "AUDUSD": { symbol_id: 105, name: "AUD/USD", base_price: 0.6578, group: "Forex Real", volatility: 0.002 },
    "USDCAD": { symbol_id: 106, name: "USD/CAD", base_price: 1.3489, group: "Forex Real", volatility: 0.002 },
    "EURGBP": { symbol_id: 107, name: "EUR/GBP", base_price: 0.8592, group: "Forex Real", volatility: 0.0015 },
    "EURJPY": { symbol_id: 108, name: "EUR/JPY", base_price: 161.25, group: "Forex Real", volatility: 0.003 },
    "GBPJPY": { symbol_id: 109, name: "GBP/JPY", base_price: 187.45, group: "Forex Real", volatility: 0.003 },
    "AUDJPY": { symbol_id: 110, name: "AUD/JPY", base_price: 97.58, group: "Forex Real", volatility: 0.003 },
    "EURCHF": { symbol_id: 111, name: "EUR/CHF", base_price: 0.9532, group: "Forex Real", volatility: 0.0015 },
    "GBPCHF": { symbol_id: 112, name: "GBP/CHF", base_price: 1.1085, group: "Forex Real", volatility: 0.002 },
    "AUDCAD": { symbol_id: 113, name: "AUD/CAD", base_price: 0.8876, group: "Forex Real", volatility: 0.002 },
    "AUDNZD": { symbol_id: 114, name: "AUD/NZD", base_price: 1.0785, group: "Forex Real", volatility: 0.0015 },
    "CADJPY": { symbol_id: 115, name: "CAD/JPY", base_price: 109.95, group: "Forex Real", volatility: 0.003 },
    "CHFJPY": { symbol_id: 116, name: "CHF/JPY", base_price: 169.23, group: "Forex Real", volatility: 0.003 },
    "EURAUD": { symbol_id: 117, name: "EUR/AUD", base_price: 1.6532, group: "Forex Real", volatility: 0.002 },
    "EURCAD": { symbol_id: 118, name: "EUR/CAD", base_price: 1.4678, group: "Forex Real", volatility: 0.002 },
    "GBPAUD": { symbol_id: 119, name: "GBP/AUD", base_price: 1.9234, group: "Forex Real", volatility: 0.002 },
    "GBPCAD": { symbol_id: 120, name: "GBP/CAD", base_price: 1.7056, group: "Forex Real", volatility: 0.002 },

    // Forex OTC Pairs
    "EURUSD_otc": { symbol_id: 201, name: "EUR/USD (OTC)", base_price: 1.0876, group: "Forex OTC", volatility: 0.0025 },
    "GBPUSD_otc": { symbol_id: 202, name: "GBP/USD (OTC)", base_price: 1.2645, group: "Forex OTC", volatility: 0.0025 },
    "USDJPY_otc": { symbol_id: 203, name: "USD/JPY (OTC)", base_price: 148.32, group: "Forex OTC", volatility: 0.0035 },
    "USDCHF_otc": { symbol_id: 204, name: "USD/CHF (OTC)", base_price: 0.8765, group: "Forex OTC", volatility: 0.0025 },
    "AUDUSD_otc": { symbol_id: 205, name: "AUD/USD (OTC)", base_price: 0.6578, group: "Forex OTC", volatility: 0.0025 },
    "USDCAD_otc": { symbol_id: 206, name: "USD/CAD (OTC)", base_price: 1.3489, group: "Forex OTC", volatility: 0.0025 },
    "EURGBP_otc": { symbol_id: 207, name: "EUR/GBP (OTC)", base_price: 0.8592, group: "Forex OTC", volatility: 0.002 },
    "EURNZD_otc": { symbol_id: 208, name: "EUR/NZD (OTC)", base_price: 1.7923, group: "Forex OTC", volatility: 0.0025 },
    "EURJPY_otc": { symbol_id: 209, name: "EUR/JPY (OTC)", base_price: 161.25, group: "Forex OTC", volatility: 0.0035 },
    "GBPJPY_otc": { symbol_id: 210, name: "GBP/JPY (OTC)", base_price: 187.45, group: "Forex OTC", volatility: 0.0035 },
    "AUDJPY_otc": { symbol_id: 211, name: "AUD/JPY (OTC)", base_price: 97.58, group: "Forex OTC", volatility: 0.0035 },
    "EURCHF_otc": { symbol_id: 212, name: "EUR/CHF (OTC)", base_price: 0.9532, group: "Forex OTC", volatility: 0.002 },
    "EURSGD_otc": { symbol_id: 213, name: "EUR/SGD (OTC)", base_price: 1.4523, group: "Forex OTC", volatility: 0.002 },
    "GBPCHF_otc": { symbol_id: 214, name: "GBP/CHF (OTC)", base_price: 1.1085, group: "Forex OTC", volatility: 0.0025 },
    "NZDUSD_otc": { symbol_id: 215, name: "NZD/USD (OTC)", base_price: 0.6098, group: "Forex OTC", volatility: 0.0025 },
    "NZDCHF_otc": { symbol_id: 216, name: "NZD/CHF (OTC)", base_price: 0.5342, group: "Forex OTC", volatility: 0.002 },
    "NZDCAD_otc": { symbol_id: 217, name: "NZD/CAD (OTC)", base_price: 0.8223, group: "Forex OTC", volatility: 0.002 },
    "NZDJPY_otc": { symbol_id: 218, name: "NZD/JPY (OTC)", base_price: 90.45, group: "Forex OTC", volatility: 0.0035 },
    "AUDCAD_otc": { symbol_id: 219, name: "AUD/CAD (OTC)", base_price: 0.8876, group: "Forex OTC", volatility: 0.0025 },
    "AUDNZD_otc": { symbol_id: 220, name: "AUD/NZD (OTC)", base_price: 1.0785, group: "Forex OTC", volatility: 0.002 },
    "CADJPY_otc": { symbol_id: 221, name: "CAD/JPY (OTC)", base_price: 109.95, group: "Forex OTC", volatility: 0.0035 },
    "CHFJPY_otc": { symbol_id: 222, name: "CHF/JPY (OTC)", base_price: 169.23, group: "Forex OTC", volatility: 0.0035 },
    "EURAUD_otc": { symbol_id: 223, name: "EUR/AUD (OTC)", base_price: 1.6532, group: "Forex OTC", volatility: 0.0025 },
    "EURCAD_otc": { symbol_id: 224, name: "EUR/CAD (OTC)", base_price: 1.4678, group: "Forex OTC", volatility: 0.0025 },
    "GBPAUD_otc": { symbol_id: 225, name: "GBP/AUD (OTC)", base_price: 1.9234, group: "Forex OTC", volatility: 0.0025 },
    "GBPNZD_otc": { symbol_id: 226, name: "GBP/NZD (OTC)", base_price: 2.0745, group: "Forex OTC", volatility: 0.0025 },
    "GBPCAD_otc": { symbol_id: 227, name: "GBP/CAD (OTC)", base_price: 1.7056, group: "Forex OTC", volatility: 0.0025 },
    "USDBDT_otc": { symbol_id: 228, name: "USD/BDT (OTC)", base_price: 109.50, group: "Forex OTC", volatility: 0.004 },
    "BRLUSD_otc": { symbol_id: 332, name: "USD/BRL (OTC)", base_price: 0.1896, group: "Forex OTC", volatility: 0.004 },
    "USDINR_otc": { symbol_id: 229, name: "USD/INR (OTC)", base_price: 83.25, group: "Forex OTC", volatility: 0.003 },
    "USDARS_otc": { symbol_id: 230, name: "USD/ARS (OTC)", base_price: 870.25, group: "Forex OTC", volatility: 0.005 },
    "USDPHP_otc": { symbol_id: 231, name: "USD/PHP (OTC)", base_price: 56.35, group: "Forex OTC", volatility: 0.003 },
    "USDPKR_otc": { symbol_id: 232, name: "USD/PKR (OTC)", base_price: 278.50, group: "Forex OTC", volatility: 0.004 },
    "USDMXN_otc": { symbol_id: 233, name: "USD/MXN (OTC)", base_price: 17.25, group: "Forex OTC", volatility: 0.004 },
    "USDCOP_otc": { symbol_id: 234, name: "USD/COP (OTC)", base_price: 3925.50, group: "Forex OTC", volatility: 0.005 },
    "USDEGP_otc": { symbol_id: 235, name: "USD/EGP (OTC)", base_price: 47.80, group: "Forex OTC", volatility: 0.003 },
    "USDTRY_otc": { symbol_id: 236, name: "USD/TRY (OTC)", base_price: 32.45, group: "Forex OTC", volatility: 0.005 },
    "USDDZD_otc": { symbol_id: 237, name: "USD/DZD (OTC)", base_price: 134.50, group: "Forex OTC", volatility: 0.003 },
    "USDIDR_otc": { symbol_id: 238, name: "USD/IDR (OTC)", base_price: 15750, group: "Forex OTC", volatility: 0.004 },
    "USDZAR_otc": { symbol_id: 239, name: "USD/ZAR (OTC)", base_price: 18.95, group: "Forex OTC", volatility: 0.005 },

    // Commodities
    "XAUUSD": { symbol_id: 301, name: "Gold", base_price: 2150.50, group: "Commodities", volatility: 0.008 },
    "XAGUSD": { symbol_id: 302, name: "Silver", base_price: 25.75, group: "Commodities", volatility: 0.01 },
    "XBRUSD": { symbol_id: 303, name: "Brent Oil", base_price: 85.30, group: "Commodities", volatility: 0.015 },
    "XTIUSD": { symbol_id: 304, name: "WTI Oil", base_price: 81.20, group: "Commodities", volatility: 0.015 },
    "NATGAS": { symbol_id: 305, name: "Natural Gas", base_price: 2.75, group: "Commodities", volatility: 0.02 },

    // Commodities OTC
    "UKBrent_otc": { symbol_id: 306, name: "UK Brent Oil (OTC)", base_price: 85.30, group: "Commodities OTC", volatility: 0.018 },
    "USCrude_otc": { symbol_id: 307, name: "US Crude Oil (OTC)", base_price: 81.20, group: "Commodities OTC", volatility: 0.018 },
    "XAUUSD_otc": { symbol_id: 308, name: "Gold (OTC)", base_price: 2150.50, group: "Commodities OTC", volatility: 0.01 },
    "XAGUSD_otc": { symbol_id: 309, name: "Silver (OTC)", base_price: 25.75, group: "Commodities OTC", volatility: 0.012 },

    // Cryptocurrencies
    "BTCUSD_otc": { symbol_id: 401, name: "Bitcoin (OTC)", base_price: 65400, group: "Crypto", volatility: 0.025 },
    "ARBUSD_otc": { symbol_id: 402, name: "Arbitrum (OTC)", base_price: 1.85, group: "Crypto", volatility: 0.03 },
    "AXIUSD_otc": { symbol_id: 403, name: "Axie Infinity (OTC)", base_price: 8.75, group: "Crypto", volatility: 0.03 },
    "HAMUSD_otc": { symbol_id: 404, name: "Hamster (OTC)", base_price: 0.0045, group: "Crypto", volatility: 0.04 },
    "SHIUSD_otc": { symbol_id: 405, name: "Shiba Inu (OTC)", base_price: 0.000024, group: "Crypto", volatility: 0.04 },
    "ETHUSD_otc": { symbol_id: 406, name: "Ethereum (OTC)", base_price: 3450, group: "Crypto", volatility: 0.022 },
    "CRLUSD_otc": { symbol_id: 407, name: "Cardano (OTC)", base_price: 0.58, group: "Crypto", volatility: 0.03 },
    "BNBUSD_otc": { symbol_id: 408, name: "Binance Coin (OTC)", base_price: 410, group: "Crypto", volatility: 0.022 },
    "XRPUSD_otc": { symbol_id: 409, name: "Ripple (OTC)", base_price: 0.62, group: "Crypto", volatility: 0.03 },
    "LTCUSD_otc": { symbol_id: 410, name: "Litecoin (OTC)", base_price: 85.50, group: "Crypto", volatility: 0.025 },
    "DOGUSD_otc": { symbol_id: 411, name: "Dogecoin (OTC)", base_price: 0.15, group: "Crypto", volatility: 0.035 },
    "TRXUSD_otc": { symbol_id: 412, name: "TRON (OTC)", base_price: 0.12, group: "Crypto", volatility: 0.03 },
    "PEPUSD_otc": { symbol_id: 413, name: "Pepe (OTC)", base_price: 0.0000085, group: "Crypto", volatility: 0.045 },
    "GALUSD_otc": { symbol_id: 414, name: "Gala (OTC)", base_price: 0.035, group: "Crypto", volatility: 0.035 },
    "TRUUSD_otc": { symbol_id: 415, name: "Trump (OTC)", base_price: 2.45, group: "Crypto", volatility: 0.03 },
    "BONUSD_otc": { symbol_id: 416, name: "Bonk (OTC)", base_price: 0.000023, group: "Crypto", volatility: 0.04 },
    "MANUSD_otc": { symbol_id: 417, name: "Decentraland (OTC)", base_price: 0.55, group: "Crypto", volatility: 0.03 },
    "MELUSD_otc": { symbol_id: 418, name: "Melania Meme (OTC)", base_price: 1.85, group: "Crypto", volatility: 0.035 },
    "APTUSD_otc": { symbol_id: 419, name: "Aptos (OTC)", base_price: 9.75, group: "Crypto", volatility: 0.028 },
    "AVAUSD_otc": { symbol_id: 420, name: "Avalanche (OTC)", base_price: 38.50, group: "Crypto", volatility: 0.028 },
    "BCHUSD_otc": { symbol_id: 421, name: "Bitcoin Cash (OTC)", base_price: 425, group: "Crypto", volatility: 0.025 },
    "DOTUSD_otc": { symbol_id: 422, name: "Polkadot (OTC)", base_price: 8.95, group: "Crypto", volatility: 0.028 },
    "LINUSD_otc": { symbol_id: 423, name: "Chainlink (OTC)", base_price: 18.25, group: "Crypto", volatility: 0.028 },
    "ATOUSD_otc": { symbol_id: 424, name: "Cosmos (OTC)", base_price: 11.50, group: "Crypto", volatility: 0.028 },
    "SOLUSD_otc": { symbol_id: 425, name: "Solana (OTC)", base_price: 175, group: "Crypto", volatility: 0.026 },
    "ADAUSD_otc": { symbol_id: 426, name: "Cardano (OTC)", base_price: 0.58, group: "Crypto", volatility: 0.03 },
    "TONUSD_otc": { symbol_id: 427, name: "Toncoin (OTC)", base_price: 6.85, group: "Crypto", volatility: 0.028 },
    "FLOUSD_otc": { symbol_id: 428, name: "Floki (OTC)", base_price: 0.00023, group: "Crypto", volatility: 0.04 },
    "DASUSD_otc": { symbol_id: 429, name: "Dash (OTC)", base_price: 32.50, group: "Crypto", volatility: 0.025 },
    "BEAUSD_otc": { symbol_id: 430, name: "Beam (OTC)", base_price: 0.022, group: "Crypto", volatility: 0.035 },

    // Stocks
    "MSFT_otc": { symbol_id: 501, name: "Microsoft (OTC)", base_price: 420, group: "Stocks", volatility: 0.015 },
    "PFE_otc": { symbol_id: 502, name: "Pfizer (OTC)", base_price: 28.50, group: "Stocks", volatility: 0.015 },
    "BA_otc": { symbol_id: 503, name: "Boeing (OTC)", base_price: 185, group: "Stocks", volatility: 0.018 },
    "JNJ_otc": { symbol_id: 504, name: "Johnson & Johnson (OTC)", base_price: 158, group: "Stocks", volatility: 0.012 },
    "INTC_otc": { symbol_id: 505, name: "Intel (OTC)", base_price: 42.50, group: "Stocks", volatility: 0.016 },
    "MCD_otc": { symbol_id: 506, name: "McDonald's (OTC)", base_price: 285, group: "Stocks", volatility: 0.012 },
    "AXP_otc": { symbol_id: 507, name: "American Express (OTC)", base_price: 225, group: "Stocks", volatility: 0.014 },
    "FB_otc": { symbol_id: 508, name: "Facebook (OTC)", base_price: 485, group: "Stocks", volatility: 0.016 }
};

// ==================== HELPER FUNCTIONS ====================
function getCurrentBDTime() {
    const now = new Date();
    // Convert to UTC+6 (Bangladesh Time)
    const bdTime = new Date(now.getTime() + (6 * 60 * 60 * 1000));
    return bdTime;
}

function formatPrice(price, assetSymbol) {
    const asset = ASSETS[assetSymbol];
    if (!asset) return price;

    if (asset.group === "Crypto") {
        if (price < 0.01) return Number(price.toFixed(8));
        if (price < 1) return Number(price.toFixed(6));
        return Number(price.toFixed(2));
    }
    if (assetSymbol.startsWith("XAU")) return Number(price.toFixed(2));
    if (price > 1000) return Number(price.toFixed(2));
    if (price > 100) return Number(price.toFixed(3));
    if (price > 10) return Number(price.toFixed(4));
    return Number(price.toFixed(5));
}

function generateCandles(assetSymbol, limit = 100) {
    const asset = ASSETS[assetSymbol];
    if (!asset) return [];

    const candles = [];
    const now = getCurrentBDTime();
    const basePrice = asset.base_price;
    const volatility = asset.volatility;

    for (let i = 0; i < limit; i++) {
        const candleTime = new Date(now.getTime() - (i * 60 * 1000));
        const minuteSeed = candleTime.getMinutes() + (candleTime.getHours() * 60);

        // Create deterministic but realistic price movement
        const seed = (minuteSeed + asset.symbol_id) % 1000;
        const change = (Math.sin(seed) * volatility) + (Math.random() - 0.5) * volatility * 0.5;

        const openPrice = basePrice * (1 + (minuteSeed * 0.00005));
        const closePrice = openPrice * (1 + change);
        const highPrice = Math.max(openPrice, closePrice) * (1 + Math.random() * volatility * 0.5);
        const lowPrice = Math.min(openPrice, closePrice) * (1 - Math.random() * volatility * 0.5);

        // Generate signal based on price movement
        let direction = "NEUTRAL";
        let signal = "NEUTRAL";
        let confidence = 50;

        if (change > volatility * 0.5) {
            direction = "CALL";
            signal = "BUY";
            confidence = 65 + Math.floor(Math.random() * 25);
        } else if (change < -volatility * 0.5) {
            direction = "PUT";
            signal = "SELL";
            confidence = 65 + Math.floor(Math.random() * 25);
        }

        candles.push({
            symbol_id: asset.symbol_id,
            time: Math.floor(candleTime.getTime() / 1000),
            open: formatPrice(openPrice, assetSymbol),
            close: formatPrice(closePrice, assetSymbol),
            high: formatPrice(highPrice, assetSymbol),
            low: formatPrice(lowPrice, assetSymbol),
            ticks: 50 + Math.floor(Math.random() * 150),
            last_tick: Date.now() / 1000,
            asset: assetSymbol,
            asset_name: asset.name,
            time_read: candleTime.toISOString().replace('T', ' ').substring(0, 16) + ' (UTC: +06:00)',
            direction: direction,
            signal: signal,
            trend: change > 0 ? "UP" : "DOWN",
            confidence: confidence,
            signal_type: confidence >= 75 ? `STRONG_${signal}` : (confidence >= 60 ? signal : "HOLD")
        });
    }

    return candles.reverse(); // Oldest first
}

// ==================== NEWS DATA ====================
const forexNews = [
    { id: 1, title: "Federal Reserve Maintains Interest Rates", impact: "HIGH", currency: "USD", content: "Fed keeps rates steady at 5.25-5.50% as expected. Dovish tilt in statement." },
    { id: 2, title: "ECB Signals June Rate Cut Possibility", impact: "MEDIUM", currency: "EUR", content: "European Central Bank minutes show growing support for rate cut in June." },
    { id: 3, title: "UK GDP Beats Expectations", impact: "HIGH", currency: "GBP", content: "UK economy grows 0.3% in Q1, surpassing forecasts of 0.1%." },
    { id: 4, title: "BOJ Maintains Ultra-Loose Policy", impact: "MEDIUM", currency: "JPY", content: "Bank of Japan keeps negative rates, yen weakens slightly." },
    { id: 5, title: "BDT Shows Stability Amid Regional Volatility", impact: "LOW", currency: "BDT", content: "Bangladeshi Taka remains stable against USD despite regional pressures." }
];

// ==================== MAIN WORKER HANDLER ====================
export default {
    async fetch(request) {
        const url = new URL(request.url);
        const path = url.pathname;

        // CORS headers
        const corsHeaders = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Content-Type': 'application/json'
        };

        if (request.method === 'OPTIONS') {
            return new Response(null, { headers: corsHeaders });
        }

        // ==================== QUOTEX CANDLES ENDPOINT ====================
        if (path === '/quotex_candles') {
            const asset = url.searchParams.get('assets') || 'BRLUSD_otc';
            const limit = parseInt(url.searchParams.get('limit')) || 100;

            if (!ASSETS[asset]) {
                return new Response(JSON.stringify({ error: `Asset '${asset}' not found` }, null, 2), {
                    status: 404,
                    headers: corsHeaders
                });
            }

            const candles = generateCandles(asset, limit);
            return new Response(JSON.stringify(candles, null, 2), { headers: corsHeaders });
        }

        // ==================== QUOTEX SIGNAL ENDPOINT ====================
        if (path === '/quotex_signal') {
            const asset = url.searchParams.get('assets') || 'EURUSD_otc';

            if (!ASSETS[asset]) {
                return new Response(JSON.stringify({ error: `Asset '${asset}' not found` }, null, 2), {
                    status: 404,
                    headers: corsHeaders
                });
            }

            const candles = generateCandles(asset, 5);
            const latest = candles[candles.length - 1];

            const signalData = {
                direction: latest.direction,
                signal: latest.signal,
                trend: latest.trend,
                confidence: latest.confidence,
                signal_type: latest.signal_type,
                current_price: latest.close,
                asset: asset,
                asset_name: ASSETS[asset].name,
                time: Math.floor(Date.now() / 1000),
                time_read: getCurrentBDTime().toISOString().replace('T', ' ').substring(0, 16) + ' (UTC: +06:00)'
            };

            return new Response(JSON.stringify(signalData, null, 2), { headers: corsHeaders });
        }

        // ==================== ASSETS ENDPOINT ====================
        if (path === '/assets') {
            const assetsList = Object.entries(ASSETS).map(([key, value]) => ({
                value: key,
                label: value.name,
                group: value.group,
                symbol_id: value.symbol_id
            }));
            assetsList.sort((a, b) => a.group.localeCompare(b.group) || a.symbol_id - b.symbol_id);
            return new Response(JSON.stringify(assetsList, null, 2), { headers: corsHeaders });
        }

        // ==================== FOREX NEWS ENDPOINT ====================
        if (path === '/forex_factory/news') {
            const now = getCurrentBDTime();
            const newsWithTime = forexNews.map((news, index) => ({
                ...news,
                time: new Date(now.getTime() - (index * 3600000)).toISOString().replace('T', ' ').substring(0, 16)
            }));

            return new Response(JSON.stringify({
                news: newsWithTime,
                last_updated: now.toISOString(),
                source: "Forex Factory (Simulated)"
            }, null, 2), { headers: corsHeaders });
        }

        // ==================== MARKET STATUS ENDPOINT ====================
        if (path.startsWith('/market_status/')) {
            const asset = path.split('/')[2];

            if (!ASSETS[asset]) {
                return new Response(JSON.stringify({ error: "Asset not found" }, null, 2), {
                    status: 404,
                    headers: corsHeaders
                });
            }

            const now = getCurrentBDTime();
            const isWeekend = now.getDay() === 0 || now.getDay() === 6;
            const isCrypto = ASSETS[asset].group === "Crypto";

            return new Response(JSON.stringify({
                asset: asset,
                market_open: isCrypto ? true : !isWeekend,
                reason: isCrypto ? "Cryptocurrency markets trade 24/7" : (isWeekend ? "Weekend - Forex markets closed" : "Market is open"),
                current_time: now.toISOString().replace('T', ' ').substring(0, 16) + ' (UTC: +06:00)'
            }, null, 2), { headers: corsHeaders });
        }

        // ==================== HOME PAGE ====================
        if (path === '/' || path === '') {
            const now = getCurrentBDTime();
            const totalAssets = Object.keys(ASSETS).length;

            const html = `<!DOCTYPE html>
            <html>
            <head>
                <title>JUMMUUBOT PRO TRADING API</title>
                <style>
                    body { font-family: Arial; max-width: 1200px; margin: 50px auto; padding: 20px; background: #082602; }
                    h1 { color: #f1f7f0; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
                    .current-time { background: #2c3e50; color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
                    .stats { display: flex; flex-wrap: wrap; gap: 10px; margin: 20px 0; }
                    .stat-card { background: red; padding: 15px; border-radius: 8px; flex: 1; min-width: 150px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                    .stat-number { font-size: 24px; font-weight: bold; color: #3498db; }
                    .endpoint { background: olive; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                    .new { background: #27ae60; color: white; padding: 3px 10px; border-radius: 15px; font-size: 12px; }
                    code { background: #ecf0f1; padding: 3px 8px; border-radius: 5px; }
                    pre { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 8px; overflow-x: auto; }
                </style>
            </head>
            <body>
                <h1> JUMMUUBOT PRO TRADING API</h1>
                <div class="current-time"> Bangladesh Time: <strong>${now.toISOString().replace('T', ' ').substring(0, 19)}</strong></div>
                <div class="stats">
                    <div class="stat-card"><div class="stat-number">${totalAssets}</div><div>Total Trading Pairs</div></div>
                    <div class="stat-card"><div class="stat-number">100+</div><div>Default Candles</div></div>
                    <div class="stat-card"><div class="stat-number">24/7</div><div>Crypto Trading</div></div>
                </div>

                <div class="endpoint">
                    <span class="new">NEW</span>
                    <h3> Get 100 Candles with Signals:</h3>
                    <code>GET /quotex_candles?assets=EURUSD_otc</code><br>
                    <a href="/quotex_candles?assets=EURUSD_otc" target="_blank">Try it: EURUSD_otc (100 candles)</a>
                </div>

                <div class="endpoint">
                    <span class="new">NEW</span>
                    <h3> Get Pure Signal:</h3>
                    <code>GET /quotex_signal?assets=EURUSD_otc</code><br>
                    <a href="/quotex_signal?assets=EURUSD_otc" target="_blank">Try it: Current EURUSD_otc signal</a>
                </div>

                <div class="endpoint">
                    <span class="new">NEW</span>
                    <h3> Forex News:</h3>
                    <code>GET /forex_factory/news</code><br>
                    <a href="/forex_factory/news" target="_blank">View News</a>
                </div>

                <div class="endpoint">
                    <span class="new">NEW</span>
                    <h3> Market Status Check:</h3>
                    <code>GET /market_status/EURUSD_otc</code><br>
                    <a href="/market_status/EURUSD_otc" target="_blank">Check EURUSD_otc</a>
                </div>

                <div class="endpoint">
                    <h3> All Assets:</h3>
                    <code>GET /assets</code><br>
                    <a href="/assets" target="_blank">View all ${totalAssets} pairs</a>
                </div>

                <p> <strong>Total Assets:</strong> ${totalAssets}</p>
                <p> <strong>Default Candles:</strong> 100 (for proper trend analysis)</p>

            </body>
            </html>`;

            return new Response(html, { headers: { 'Content-Type': 'text/html' } });
        }

        // 404 for unknown routes
        return new Response(JSON.stringify({ error: "Endpoint not found" }, null, 2), { status: 404, headers: corsHeaders });
    }
};