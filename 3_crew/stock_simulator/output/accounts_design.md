# Indian Stock Market Trading Simulation Platform – Backend Engineering Design

## Executive Summary

This document specifies a complete, self-contained backend design for an Indian stock market trading simulation platform. The backend is a single-file Python module (`accounts.py`) exposing one main class (`Account`) with deterministic fixed stock prices, transaction tracking, holdings management, and comprehensive reporting for portfolio analysis.

---

## Architecture Overview

### Design Principles
- **Deterministic**: Fixed prices, no external data, reproducible behavior
- **Testable**: Pure functions, explicit state management, no side effects outside the Account object
- **Compact**: ~250–420 lines of implementation code
- **Self-Contained**: Standard library only, no external dependencies
- **Separation of Concerns**: Backend logic only; UI and testing are separate layers

### Core Components
1. **Fixed Price Provider** – Hardcoded NSE prices for Indian stocks
2. **Cash Management** – Deposits, withdrawals, balance tracking
3. **Holdings Management** – Per-symbol ownership, cost basis, current value
4. **Transaction Ledger** – Complete audit trail with charges breakdown
5. **Reporting Engine** – Summary, portfolio, holdings, history, P&L calculations
6. **Validation Layer** – Symbol format, quantity, amounts, balance checks

---

## Data Structures

### 1. Fixed Price Registry

**Structure**: Dictionary mapping normalized symbols to INR prices.

```
SYMBOL -> PRICE (float, INR)

Examples:
RELIANCE.NS -> 2850.00
RELIANCE.BO -> 2850.00 (same price)
TCS.NS -> 3900.00
INFY.NS -> 1500.00
...
```

**Symbols Supported**:
- RELIANCE.NS, RELIANCE.BO
- TCS.NS, TCS.BO
- INFY.NS, INFY.BO
- HDFCBANK.NS, HDFCBANK.BO
- ICICIBANK.NS, ICICIBANK.BO
- SBIN.NS, SBIN.BO
- ITC.NS, ITC.BO
- TATAMOTORS.NS, TATAMOTORS.BO
- ADANIENT.NS, ADANIENT.BO
- WIPRO.NS, WIPRO.BO

**Normalization**: Always uppercase; accept both .NS and .BO; treat as equivalent by base name.

---

### 2. Holdings Model

**Per-Symbol Holding**: Dictionary entry per symbol with:

```python
{
  "symbol": str,           # Normalized symbol (e.g., "RELIANCE.NS")
  "quantity": int,         # Current quantity owned (>= 0)
  "avg_buy_price": float,  # Weighted average purchase price (INR)
  "total_invested": float, # Total cash spent on current holdings (INR)
  "current_price": float,  # Latest market price from provider (INR)
  "current_value": float,  # Quantity × current_price (INR)
  "unrealized_pl": float,  # Current_value - total_invested (INR)
}
```

**Holdings Container**: Dictionary `holdings = {symbol: holding_dict, ...}`

**Update Logic**:
- On buy: Recalculate weighted average price, update total invested.
- On sell: Reduce quantity; if quantity reaches 0, remove holding.
- On price change: Recalculate current_value and unrealized_pl.

---

### 3. Transaction Model

**Transaction Record** (returned as plain dict):

```python
{
  "transaction_id": str,        # Unique ID (e.g., "TXN_001")
  "timestamp": str,             # ISO-format datetime string
  "type": str,                  # "DEPOSIT", "WITHDRAW", "BUY", "SELL"
  "symbol": str | None,         # Symbol for buy/sell; None for deposit/withdraw
  "exchange": str | None,       # "NSE" or "BSE" for buy/sell; None for cash ops
  "quantity": int | None,       # For buy/sell only
  "price": float | None,        # Price per share for buy/sell (INR)
  "gross_amount": float,        # Gross value before charges (INR)
  "charges": float,             # Total charges applied (INR)
  "net_amount": float,          # Final cash impact (INR), signed
  "notes": str,                 # Optional user annotation
}
```

**Transaction Container**: List `transactions = [txn_dict, ...]`

---

### 4. Account State Model

**Instance Variables**:

```python
class Account:
  owner_name: str               # Account owner
  email: str | None             # Optional email
  cash_balance: float           # Current available cash (INR)
  total_deposits: float         # Sum of all deposits (INR)
  total_withdrawals: float      # Sum of all withdrawals (INR)
  net_cash_invested: float      # total_deposits - total_withdrawals (INR)
  holdings: dict                # {symbol: holding_dict}
  transactions: list            # List of transaction dicts
  _transaction_counter: int     # For ID generation (TXN_001, TXN_002, ...)
```

---

## Validation Rules

### Symbol Validation
- **Format**: `SYMBOL.NS` or `SYMBOL.BO`
- **Rules**:
  - Must be exactly 2 parts separated by a single dot.
  - First part (symbol): alphanumeric, uppercase, 1–8 characters.
  - Second part (exchange): exactly "NS" or "BO".
  - Must exist in the fixed price provider.
- **Normalization**: Convert to uppercase; normalize both .NS and .BO.

### Quantity Validation
- Must be a positive integer (> 0).
- Raise ValueError if not an integer or if <= 0.

### Amount Validation
- Must be a positive number (float or int).
- Raise ValueError if <= 0.

### Cash Balance Rules
- Deposits increase balance; withdrawals decrease balance.
- Prevent withdrawals that would create negative balance.
- Buying reduces balance; prevent if insufficient cash.
- Selling increases balance.

### Holdings Rules
- Prevent selling more shares than owned (quantity > current holding).
- Prevent selling a symbol with zero holding.

---

## Trading Charges Model

### Charge Components

Charges are calculated per trade as follows:

```
Gross Amount = Quantity × Price

Charges:
  - Brokerage: 0.1% of gross amount
  - Exchange Charge: 0.01% of gross amount
  - GST-style Charge: 18% of (Brokerage + Exchange Charge)
  - Stamp Duty: 0.01% of gross amount

Total Charges = Brokerage + Exchange Charge + GST + Stamp Duty

Net Amount (buy) = Gross Amount + Total Charges
Net Amount (sell) = Gross Amount - Total Charges
```

### Implementation Strategy
- Charge rates configurable as class-level constants.
- Deterministic; no randomness.
- Applied to all buy/sell transactions.
- Recorded explicitly in transaction record.
- Affect cash balance immediately upon trade.

---

## Buy/Sell Logic

### Buy Transaction Flow
1. **Validate**: Symbol, quantity > 0.
2. **Calculate**: Gross = Quantity × Price; charges; net cash needed.
3. **Check Balance**: Ensure cash_balance >= net cash needed.
4. **Update Holdings**:
   - If symbol exists: Recalculate weighted average price.
   - If symbol new: Create holding entry.
   - Formula: `new_avg_price = (old_qty × old_avg + qty × price) / (old_qty + qty)`
5. **Update Cash**: Reduce by net amount.
6. **Record Transaction**: Create txn_dict, append to transactions list.
7. **Return**: Success dict with txn_id, net_amount, new_balance, new_holding.

### Sell Transaction Flow
1. **Validate**: Symbol, quantity > 0, holding exists, quantity <= held quantity.
2. **Calculate**: Gross = Quantity × Current_Price; charges; net cash received.
3. **Update Holdings**:
   - Reduce quantity.
   - If quantity reaches 0, remove holding.
   - Otherwise, keep avg_buy_price unchanged (for future P&L).
4. **Track Realized P&L**: 
   - Realized_PL = (Current_Price - Avg_Buy_Price) × Quantity
   - Store in transaction record or separate P&L tracker.
5. **Update Cash**: Increase by net amount.
6. **Record Transaction**: Create txn_dict, append to transactions list.
7. **Return**: Success dict with txn_id, net_amount, new_balance, realized_pl.

---

## Average Price Calculation

### Weighted Average Buy Price (WABP)

Used to track cost basis for holdings.

```
WABP = (Previous Total Invested + New Purchase Value) / (Previous Quantity + New Quantity)

Where:
  New Purchase Value = Quantity × Price (gross, before charges)
  Previous Total Invested = Previous Quantity × Previous WABP
```

### Application
- Initialized on first buy of a symbol.
- Updated on every subsequent buy.
- Unchanged on sells.
- Used in P&L calculations.

---

## P&L Calculation

### Unrealized P&L (Per Holding)

```
Unrealized_PL = (Current_Price - Avg_Buy_Price) × Current_Quantity

Where:
  Current_Price = From fixed price provider
  Avg_Buy_Price = Weighted average purchase price
  Current_Quantity = Shares currently held
```

### Realized P&L (Per Sell Trade)

```
Realized_PL = (Sell_Price - Avg_Buy_Price) × Sold_Quantity

Cumulative Realized_PL = Sum of realized_pl from all sell transactions
```

### Total P&L (Entire Portfolio)

```
Total_PL = Total_Portfolio_Value - Net_Cash_Invested

Where:
  Total_Portfolio_Value = Cash_Balance + Sum(Holdings Current Value)
  Net_Cash_Invested = Total_Deposits - Total_Withdrawals
```

### Total Return Percentage

```
Total_Return_Pct = (Total_PL / Net_Cash_Invested) × 100

Special Cases:
  - If Net_Cash_Invested == 0: Return 0.0 or "N/A"
  - If Net_Cash_Invested < 0: Return value may be negative
```

---

## Fixed Price Provider

### Implementation Approach

**Static Price Dictionary** (class-level constant):

```python
FIXED_PRICES = {
    "RELIANCE.NS": 2850.00,
    "RELIANCE.BO": 2850.00,
    "TCS.NS": 3900.00,
    "TCS.BO": 3900.00,
    "INFY.NS": 1500.00,
    "INFY.BO": 1500.00,
    "HDFCBANK.NS": 1650.00,
    "HDFCBANK.BO": 1650.00,
    "ICICIBANK.NS": 1100.00,
    "ICICIBANK.BO": 1100.00,
    "SBIN.NS": 750.00,
    "SBIN.BO": 750.00,
    "ITC.NS": 430.00,
    "ITC.BO": 430.00,
    "TATAMOTORS.NS": 950.00,
    "TATAMOTORS.BO": 950.00,
    "ADANIENT.NS": 3200.00,
    "ADANIENT.BO": 3200.00,
    "WIPRO.NS": 500.00,
    "WIPRO.BO": 500.00,
}
```

### Methods
- `get_share_price(symbol: str) -> float`: Lookup, normalize, validate, return price or raise ValueError.
- `get_available_symbols() -> list[str]`: Return all available symbols (sorted, unique by base name, or as dict keys).

### Symbol Equivalence
- .NS and .BO are treated as the same security; holdings are **not** merged (separate entries).
- Example: Buying 10 RELIANCE.NS and 5 RELIANCE.BO creates two holdings.
- Price provider returns same price for both.

---

## Public API Contract

### Method Signatures and Return Types

#### Constructor
```python
__init__(owner_name: str = "Demo User", 
         email: str | None = None, 
         initial_deposit: float = 0.0) -> None
```
- Initializes account with owner_name and optional email.
- If initial_deposit > 0, automatically calls `deposit(initial_deposit)`.
- Raises ValueError if initial_deposit < 0.

#### Cash Operations

**deposit(amount: float, notes: str = "") -> dict**
```python
Returns:
{
  "success": bool,
  "message": str,
  "transaction_id": str,
  "amount": float,
  "new_balance": float,
  "timestamp": str,
}
```
- Adds amount to cash_balance.
- Increments total_deposits.
- Creates transaction record.
- Raises ValueError if amount <= 0.

**withdraw(amount: float, notes: str = "") -> dict**
```python
Returns:
{
  "success": bool,
  "message": str,
  "transaction_id": str,
  "amount": float,
  "new_balance": float,
  "timestamp": str,
}
```
- Subtracts amount from cash_balance.
- Increments total_withdrawals.
- Creates transaction record.
- Raises ValueError if amount <= 0 or amount > cash_balance.

#### Trading Operations

**buy(symbol: str, quantity: int, notes: str = "") -> dict**
```python
Returns:
{
  "success": bool,
  "message": str,
  "transaction_id": str,
  "symbol": str,
  "quantity": int,
  "price": float,
  "gross_amount": float,
  "charges": float,
  "net_amount": float,
  "new_balance": float,
  "avg_price": float,
  "timestamp": str,
}
```
- Purchases shares of a symbol at fixed price.
- Deducts gross + charges from cash_balance.
- Updates holdings with new average price.
- Creates transaction record.
- Raises ValueError for invalid symbol, quantity, or insufficient balance.

**sell(symbol: str, quantity: int, notes: str = "") -> dict**
```python
Returns:
{
  "success": bool,
  "message": str,
  "transaction_id": str,
  "symbol": str,
  "quantity": int,
  "price": float,
  "gross_amount": float,
  "charges": float,
  "net_amount": float,
  "new_balance": float,
  "realized_pl": float,
  "timestamp": str,
}
```
- Sells shares at fixed price.
- Adds net amount (after charges) to cash_balance.
- Updates holdings; removes if quantity reaches 0.
- Calculates realized P&L.
- Creates transaction record.
- Raises ValueError for invalid symbol, quantity, or insufficient holdings.

#### Price and Symbol Query

**get_share_price(symbol: str) -> float**
```python
Returns: float (price in INR)
```
- Normalizes symbol, validates format.
- Returns price from fixed provider.
- Raises ValueError if symbol not found or invalid format.

**get_available_symbols() -> list[str]**
```python
Returns: list[str] (sorted list of all available symbols)
```
- Returns all keys from FIXED_PRICES dict.
- Sorted alphabetically.

#### Summary Reports

**get_account_summary() -> dict**
```python
Returns:
{
  "owner_name": str,
  "email": str | None,
  "cash_balance": float,
  "total_deposits": float,
  "total_withdrawals": float,
  "net_cash_invested": float,
  "total_portfolio_value": float,
  "total_holdings_value": float,
  "total_unrealized_pl": float,
  "total_realized_pl": float,
  "total_pl": float,
  "total_return_pct": float,
  "timestamp": str,
}
```
- Comprehensive snapshot of