# from polygon import RESTClient
# from dotenv import load_dotenv
# import os
# from datetime import datetime
# import random
# from database import write_market, read_market
# from functools import lru_cache
# from datetime import timezone

# load_dotenv(override=True)

# polygon_api_key = os.getenv("POLYGON_API_KEY")
# polygon_plan = os.getenv("POLYGON_PLAN")

# is_paid_polygon = polygon_plan == "paid"
# is_realtime_polygon = polygon_plan == "realtime"


# def is_market_open() -> bool:
#     client = RESTClient(polygon_api_key)
#     market_status = client.get_market_status()
#     return market_status.market == "open"


# def get_all_share_prices_polygon_eod() -> dict[str, float]:
#     """With much thanks to student Reema R. for fixing the timezone issue with this!"""
#     client = RESTClient(polygon_api_key)

#     probe = client.get_previous_close_agg("SPY")[0]
#     last_close = datetime.fromtimestamp(probe.timestamp / 1000, tz=timezone.utc).date()

#     results = client.get_grouped_daily_aggs(last_close, adjusted=True, include_otc=False)
#     return {result.ticker: result.close for result in results}


# @lru_cache(maxsize=2)
# def get_market_for_prior_date(today):
#     market_data = read_market(today)
#     if not market_data:
#         market_data = get_all_share_prices_polygon_eod()
#         write_market(today, market_data)
#     return market_data


# def get_share_price_polygon_eod(symbol) -> float:
#     today = datetime.now().date().strftime("%Y-%m-%d")
#     market_data = get_market_for_prior_date(today)
#     return market_data.get(symbol, 0.0)


# def get_share_price_polygon_min(symbol) -> float:
#     client = RESTClient(polygon_api_key)
#     result = client.get_snapshot_ticker("stocks", symbol)
#     return result.min.close or result.prev_day.close


# def get_share_price_polygon(symbol) -> float:
#     if is_paid_polygon:
#         return get_share_price_polygon_min(symbol)
#     else:
#         return get_share_price_polygon_eod(symbol)


# def get_share_price(symbol) -> float:
#     if polygon_api_key:
#         try:
#             return get_share_price_polygon(symbol)
#         except Exception as e:
#             print(f"Was not able to use the polygon API due to {e}; using a random number")
#     return float(random.randint(1, 100))

from dotenv import load_dotenv
import os
import random
import logging
from datetime import datetime, time
from zoneinfo import ZoneInfo

import yfinance as yf

load_dotenv(override=True)

# ---------------------------------------------------------
# Compatibility variables expected by templates.py
# ---------------------------------------------------------
# Your templates.py imports these names, so we keep them.
# They no longer mean Polygon is being used.
is_paid_polygon = False
is_realtime_polygon = False


# ---------------------------------------------------------
# Market configuration
# ---------------------------------------------------------

INDIAN_EXCHANGE = os.getenv("INDIAN_EXCHANGE", "NSE").strip().upper()
CRYPTO_QUOTE_CURRENCY = os.getenv("CRYPTO_QUOTE_CURRENCY", "USD").strip().upper()

# If true, invalid/missing symbols return a fake random price instead of raising an error.
# For real testing, keep this false.
USE_RANDOM_PRICE_FALLBACK = (
    os.getenv("USE_RANDOM_PRICE_FALLBACK", "false").strip().lower() == "true"
)

INDIA_TIMEZONE = ZoneInfo("Asia/Kolkata")

# NSE/BSE normal equity market hours
MARKET_OPEN_TIME = time(9, 15)
MARKET_CLOSE_TIME = time(15, 30)

# Reduce noisy yfinance logs like "$AEM.NS: possibly delisted"
logging.getLogger("yfinance").setLevel(logging.CRITICAL)


# ---------------------------------------------------------
# Market open logic
# ---------------------------------------------------------

def is_market_open() -> bool:
    """
    Returns True if the Indian equity market is likely open.

    Checks:
    - Monday to Friday
    - 09:15 to 15:30 India time

    Note:
    This does not check NSE/BSE holidays.

    For testing, set this in .env:
    RUN_EVEN_WHEN_MARKET_IS_CLOSED=true
    """
    now = datetime.now(INDIA_TIMEZONE)

    # Monday = 0, Sunday = 6
    if now.weekday() >= 5:
        return False

    current_time = now.time()

    return MARKET_OPEN_TIME <= current_time <= MARKET_CLOSE_TIME


# ---------------------------------------------------------
# Symbol normalization
# ---------------------------------------------------------

def normalize_market_symbol(symbol: str) -> str:
    """
    Converts input symbols into Yahoo Finance-compatible symbols.

    Indian equities:
    RELIANCE      -> RELIANCE.NS
    TCS           -> TCS.NS
    INFY          -> INFY.NS
    RELIANCE.NS   -> RELIANCE.NS
    RELIANCE.BO   -> RELIANCE.BO

    Indian indexes:
    NIFTY         -> ^NSEI
    SENSEX        -> ^BSESN
    BANKNIFTY     -> ^NSEBANK

    Crypto:
    BTC           -> BTC-USD
    ETH           -> ETH-USD
    BTCUSD        -> BTC-USD
    ETHUSD        -> ETH-USD
    BTC-INR       -> BTC-INR
    """

    symbol = symbol.strip().upper().replace("$", "")

    if not symbol:
        return symbol

    # Keep already-valid Yahoo symbols as-is
    if (
        symbol.endswith(".NS")
        or symbol.endswith(".BO")
        or symbol.startswith("^")
        or symbol.endswith("-USD")
        or symbol.endswith("-INR")
        or symbol.endswith("-USDT")
    ):
        return symbol

    # Common Indian index aliases
    index_map = {
        "NIFTY": "^NSEI",
        "NIFTY50": "^NSEI",
        "NIFTY 50": "^NSEI",
        "NIFTY_50": "^NSEI",
        "SENSEX": "^BSESN",
        "BANKNIFTY": "^NSEBANK",
        "BANK NIFTY": "^NSEBANK",
        "BANK_NIFTY": "^NSEBANK",
    }

    if symbol in index_map:
        return index_map[symbol]

    # Crypto aliases
    crypto_symbols = {
        "BTC": "BTC",
        "BITCOIN": "BTC",
        "ETH": "ETH",
        "ETHEREUM": "ETH",
        "SOL": "SOL",
        "SOLANA": "SOL",
        "DOGE": "DOGE",
        "DOGECOIN": "DOGE",
        "XRP": "XRP",
        "ADA": "ADA",
        "CARDANO": "ADA",
        "BNB": "BNB",
        "AVAX": "AVAX",
        "DOT": "DOT",
        "POLKADOT": "DOT",
        "MATIC": "MATIC",
        "POLYGON": "MATIC",
        "LINK": "LINK",
        "CHAINLINK": "LINK",
        "LTC": "LTC",
        "LITECOIN": "LTC",
        "BCH": "BCH",
        "TRX": "TRX",
        "SHIB": "SHIB",
        "UNI": "UNI",
        "ATOM": "ATOM",
        "ETC": "ETC",
        "XLM": "XLM",
        "NEAR": "NEAR",
        "APT": "APT",
        "ARB": "ARB",
        "OP": "OP",
        "FIL": "FIL",
        "ICP": "ICP",
        "HBAR": "HBAR",
    }

    if symbol in crypto_symbols:
        crypto_base = crypto_symbols[symbol]
        return f"{crypto_base}-{CRYPTO_QUOTE_CURRENCY}"

    # Handle BTCUSD, ETHUSD, BTCINR, ETHINR style inputs
    for crypto_base in crypto_symbols.values():
        if symbol == f"{crypto_base}USD":
            return f"{crypto_base}-USD"
        if symbol == f"{crypto_base}INR":
            return f"{crypto_base}-INR"
        if symbol == f"{crypto_base}USDT":
            return f"{crypto_base}-USD"

    # Default to Indian equity
    if INDIAN_EXCHANGE == "BSE":
        return f"{symbol}.BO"

    return f"{symbol}.NS"


# ---------------------------------------------------------
# Price lookup
# ---------------------------------------------------------

def get_share_price_yfinance(symbol: str) -> float:
    """
    Gets the latest available price from Yahoo Finance via yfinance.

    Works for:
    - Indian NSE/BSE equities
    - Indian indexes
    - Crypto pairs such as BTC-USD or BTC-INR
    """

    yahoo_symbol = normalize_market_symbol(symbol)

    if not yahoo_symbol:
        raise ValueError("Empty symbol provided")

    ticker = yf.Ticker(yahoo_symbol)

    # Try fast_info first
    try:
        fast_info = ticker.fast_info

        price = (
            fast_info.get("last_price")
            or fast_info.get("regular_market_price")
            or fast_info.get("previous_close")
        )

        if price and float(price) > 0:
            return float(price)

    except Exception as e:
        print(f"Could not fetch fast_info for {symbol} / {yahoo_symbol}: {e}")

    # Fallback to recent history
    try:
        history = ticker.history(period="5d", interval="1d")

        if history is not None and not history.empty:
            price = history["Close"].dropna().iloc[-1]

            if price and float(price) > 0:
                return float(price)

    except Exception as e:
        print(f"Could not fetch price history for {symbol} / {yahoo_symbol}: {e}")

    raise ValueError(f"No valid price found for {symbol} / {yahoo_symbol}")


def get_share_price(symbol: str) -> float:
    """
    Public function used by market_server.py.

    Keeps the same interface as your original Polygon-based code.

    Examples:
    get_share_price("RELIANCE") -> RELIANCE.NS
    get_share_price("TCS")      -> TCS.NS
    get_share_price("BTC")      -> BTC-USD or BTC-INR depending on .env
    """

    try:
        return get_share_price_yfinance(symbol)

    except Exception as e:
        print(f"Was not able to fetch market price for {symbol}: {e}")

        if USE_RANDOM_PRICE_FALLBACK:
            print("Using random fallback price")
            return float(random.randint(100, 5000))

        raise