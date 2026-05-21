import datetime

class Account:
    PRICES = {
        "RELIANCE.NS": 2850.00, "TCS.NS": 3900.00, "INFY.NS": 1500.00,
        "HDFCBANK.NS": 1650.00, "ICICIBANK.NS": 1100.00, "SBIN.NS": 750.00,
        "ITC.NS": 430.00, "TATAMOTORS.NS": 950.00, "ADANIENT.NS": 3200.00, "WIPRO.NS": 500.00
    }
    
    # Add BO equivalents
    for symbol in list(PRICES.keys()):
        if symbol.endswith('.NS'):
            PRICES[symbol.replace('.NS', '.BO')] = PRICES[symbol]
    
    # Trading charges
    BRATE, ERATE, GRATE, SDRATE = 0.001, 0.0001, 0.18, 0.0001
    
    def __init__(self, owner_name: str = "Demo User", email: str | None = None, initial_deposit: float = 0.0):
        if initial_deposit < 0:
            raise ValueError("Initial deposit cannot be negative")
        self.owner_name, self.email = owner_name, email
        self.cash_balance = self.total_deposits = self.total_withdrawals = self.net_cash_invested = 0.0
        self.holdings, self.transactions, self._tx_counter = {}, [], 0
        if initial_deposit > 0:
            self.deposit(initial_deposit, "Initial deposit")
    
    def _gen_tx_id(self) -> str:
        self._tx_counter += 1
        return f"TXN_{self._tx_counter:03d}"
    
    def _get_ts(self) -> str:
        return datetime.datetime.now().isoformat()
    
    def _validate_sym(self, symbol: str) -> str:
        symbol = symbol.upper()
        if symbol not in self.PRICES:
            raise ValueError(f"Invalid or unsupported symbol: {symbol}")
        return symbol
    
    def _validate_qty(self, qty: int) -> None:
        if not isinstance(qty, int) or qty <= 0:
            raise ValueError("Quantity must be a positive integer")
    
    def _validate_amt(self, amt: float) -> None:
        if amt <= 0:
            raise ValueError("Amount must be positive")
    
    def _calc_charges(self, gross: float) -> float:
        brk = gross * self.BRATE
        exc = gross * self.ERATE
        gst = (brk + exc) * self.GRATE
        std = gross * self.SDRATE
        return brk + exc + gst + std
    
    def deposit(self, amt: float, notes: str = "") -> dict:
        self._validate_amt(amt)
        self.cash_balance += amt
        self.total_deposits += amt
        self.net_cash_invested += amt
        tx_id, ts = self._gen_tx_id(), self._get_ts()
        tx = {"transaction_id": tx_id, "timestamp": ts, "type": "DEPOSIT", "symbol": None,
              "exchange": None, "quantity": None, "price": None, "gross_amount": amt,
              "charges": 0.0, "net_amount": amt, "notes": notes}
        self.transactions.append(tx)
        return {"success": True, "message": "Deposit successful", "transaction_id": tx_id,
                "amount": round(amt, 2), "new_balance": round(self.cash_balance, 2), "timestamp": ts}
    
    def withdraw(self, amt: float, notes: str = "") -> dict:
        self._validate_amt(amt)
        if amt > self.cash_balance:
            raise ValueError("Insufficient funds for withdrawal")
        self.cash_balance -= amt
        self.total_withdrawals += amt
        self.net_cash_invested -= amt
        tx_id, ts = self._gen_tx_id(), self._get_ts()
        tx = {"transaction_id": tx_id, "timestamp": ts, "type": "WITHDRAW", "symbol": None,
              "exchange": None, "quantity": None, "price": None, "gross_amount": amt,
              "charges": 0.0, "net_amount": -amt, "notes": notes}
        self.transactions.append(tx)
        return {"success": True, "message": "Withdrawal successful", "transaction_id": tx_id,
                "amount": round(amt, 2), "new_balance": round(self.cash_balance, 2), "timestamp": ts}
    
    def buy(self, symbol: str, qty: int, notes: str = "") -> dict:
        symbol = self._validate_sym(symbol)
        self._validate_qty(qty)
        price = self.PRICES[symbol]
        gross = price * qty
        charges = self._calc_charges(gross)
        net = gross + charges
        if net > self.cash_balance:
            raise ValueError("Insufficient funds for purchase")
        self.cash_balance -= net
        if symbol in self.holdings:
            h = self.holdings[symbol]
            new_qty = h["quantity"] + qty
            new_total = h["total_invested"] + gross
            h.update({"quantity": new_qty, "avg_buy_price": round(new_total/new_qty, 2),
                      "total_invested": round(new_total, 2)})
        else:
            self.holdings[symbol] = {"quantity": qty, "avg_buy_price": round(price, 2),
                                     "total_invested": round(gross, 2)}
        tx_id, ts = self._gen_tx_id(), self._get_ts()
        exch = "NSE" if symbol.endswith(".NS") else "BSE"
        tx = {"transaction_id": tx_id, "timestamp": ts, "type": "BUY", "symbol": symbol,
              "exchange": exch, "quantity": qty, "price": round(price, 2),
              "gross_amount": round(gross, 2), "charges": round(charges, 2),
              "net_amount": -round(net, 2), "notes": notes}
        self.transactions.append(tx)
        return {"success": True, "message": "Purchase successful", "transaction_id": tx_id,
                "symbol": symbol, "quantity": qty, "price": round(price, 2),
                "gross_amount": round(gross, 2), "charges": round(charges, 2),
                "net_amount": -round(net, 2), "new_balance": round(self.cash_balance, 2),
                "avg_price": round(self.holdings[symbol]["avg_buy_price"], 2), "timestamp": ts}
    
    def sell(self, symbol: str, qty: int, notes: str = "") -> dict:
        symbol = self._validate_sym(symbol)
        self._validate_qty(qty)
        if symbol not in self.holdings:
            raise ValueError(f"No holdings for symbol: {symbol}")
        h = self.holdings[symbol]
        if qty > h["quantity"]:
            raise ValueError("Insufficient quantity for sale")
        price = self.PRICES[symbol]
        gross = price * qty
        charges = self._calc_charges(gross)
        net = gross - charges
        pl = (price - h["avg_buy_price"]) * qty
        self.cash_balance += net
        h["quantity"] -= qty
        if h["quantity"] == 0:
            del self.holdings[symbol]
        else:
            h["total_invested"] = h["quantity"] * h["avg_buy_price"]
        tx_id, ts = self._gen_tx_id(), self._get_ts()
        exch = "NSE" if symbol.endswith(".NS") else "BSE"
        tx = {"transaction_id": tx_id, "timestamp": ts, "type": "SELL", "symbol": symbol,
              "exchange": exch, "quantity": qty, "price": round(price, 2),
              "gross_amount": round(gross, 2), "charges": round(charges, 2),
              "net_amount": round(net, 2), "notes": notes}
        self.transactions.append(tx)
        return {"success": True, "message": "Sale successful", "transaction_id": tx_id,
                "symbol": symbol, "quantity": qty, "price": round(price, 2),
                "gross_amount": round(gross, 2), "charges": round(charges, 2),
                "net_amount": round(net, 2), "new_balance": round(self.cash_balance, 2),
                "realized_pl": round(pl, 2), "timestamp": ts}
    
    def get_share_price(self, symbol: str) -> float:
        return self.PRICES[self._validate_sym(symbol)]
    
    def get_available_symbols(self) -> list[str]:
        return sorted(list(self.PRICES.keys()))
    
    def get_price_report(self) -> list[dict]:
        return [{"symbol": s, "price": round(p, 2), 
                 "exchange": "NSE" if s.endswith(".NS") else "BSE"}
                for s, p in self.PRICES.items()]
    
    def get_account_summary(self) -> dict:
        ps = self.get_portfolio_summary()
        ts = self._get_ts()
        return {"owner_name": self.owner_name, "email": self.email,
                "cash_balance": round(self.cash_balance, 2),
                "total_deposits": round(self.total_deposits, 2),
                "total_withdrawals": round(self.total_withdrawals, 2),
                "net_cash_invested": round(self.net_cash_invested, 2),
                "total_portfolio_value": round(ps["total_portfolio_value"], 2),
                "total_holdings_value": round(ps["total_holdings_value"], 2),
                "total_unrealized_pl": round(ps["total_unrealized_pl"], 2),
                "total_realized_pl": round(ps["total_realized_pl"], 2),
                "total_pl": round(ps["total_pl"], 2),
                "total_return_pct": round(ps["total_return_pct"], 2), "timestamp": ts}
    
    def get_portfolio_summary(self) -> dict:
        hr = self.get_holdings_report()
        thv = sum(h["current_value"] for h in hr)
        tupl = sum(h["unrealized_pl"] for h in hr)
        trpl = 0.0
        for t in self.transactions:
            if t["type"] == "SELL":
                s, q, sp = t["symbol"], t["quantity"], t["price"]
                abp = self.holdings[s]["avg_buy_price"] if s in self.holdings else 0
                if abp == 0:
                    bts = [x for x in self.transactions if x["type"] == "BUY" and x["symbol"] == s]
                    if bts:
                        abp = bts[-1]["price"]
                trpl += (sp - abp) * q
        tpv = self.cash_balance + thv
        tpl = tpv - self.net_cash_invested
        trpct = (tpl / self.net_cash_invested) * 100 if self.net_cash_invested != 0 else 0.0
        return {"cash_balance": round(self.cash_balance, 2),
                "total_holdings_value": round(thv, 2),
                "total_unrealized_pl": round(tupl, 2),
                "total_realized_pl": round(trpl, 2),
                "total_portfolio_value": round(tpv, 2),
                "total_pl": round(tpl, 2),
                "total_return_pct": round(trpct, 2)}
    
    def get_holdings_report(self) -> list[dict]:
        report = []
        for s, h in self.holdings.items():
            cp = self.PRICES[s]
            cv = h["quantity"] * cp
            upl = cv - h["total_invested"]
            report.append({"symbol": s, "quantity": h["quantity"],
                           "avg_buy_price": round(h["avg_buy_price"], 2),
                           "total_invested": round(h["total_invested"], 2),
                           "current_price": round(cp, 2),
                           "current_value": round(cv, 2),
                           "unrealized_pl": round(upl, 2),
                           "exchange": "NSE" if s.endswith(".NS") else "BSE"})
        return report
    
    def get_transaction_history(self) -> list[dict]:
        return [t.copy() for t in self.transactions]
    
    def get_profit_loss_report(self) -> dict:
        ps = self.get_portfolio_summary()
        return {"total_realized_pl": round(ps["total_realized_pl"], 2),
                "total_unrealized_pl": round(ps["total_unrealized_pl"], 2),
                "total_pl": round(ps["total_pl"], 2),
                "total_return_pct": round(ps["total_return_pct"], 2)}
    
    def get_all_dashboard_data(self) -> dict:
        return {"account_summary": self.get_account_summary(),
                "portfolio_summary": self.get_portfolio_summary(),
                "holdings_report": self.get_holdings_report(),
                "transaction_history": self.get_transaction_history()[:10],
                "price_report": self.get_price_report()}