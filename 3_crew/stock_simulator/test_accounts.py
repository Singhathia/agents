from accounts import Account
import unittest


class TestAccountCreation(unittest.TestCase):
    def test_account_creation_default(self):
        acc = Account()
        self.assertEqual(acc.owner_name, "Demo User")
        self.assertIsNone(acc.email)
        
    def test_account_creation_with_owner_name(self):
        acc = Account("John Doe")
        self.assertEqual(acc.owner_name, "John Doe")
        self.assertIsNone(acc.email)
        
    def test_account_creation_with_owner_name_and_email(self):
        acc = Account("John Doe", "john@example.com")
        self.assertEqual(acc.owner_name, "John Doe")
        self.assertEqual(acc.email, "john@example.com")
        
    def test_account_creation_negative_deposit(self):
        with self.assertRaises(ValueError) as context:
            Account("John Doe", "john@example.com", -100.0)
        self.assertEqual(str(context.exception), "Initial deposit cannot be negative")


class TestDepositAndWithdrawal(unittest.TestCase):
    def setUp(self):
        self.acc = Account("Test User", "test@example.com")
    
    def test_initial_deposit_through_constructor(self):
        acc = Account("Test User", "test@example.com", 5000.0)
        summary = acc.get_account_summary()
        self.assertEqual(summary["cash_balance"], 5000.0)
        self.assertEqual(summary["total_deposits"], 5000.0)
        
    def test_deposit_valid_amount(self):
        result = self.acc.deposit(1000.0, "Test deposit")
        self.assertTrue(result["success"])
        self.assertEqual(result["amount"], 1000.0)
        summary = self.acc.get_account_summary()
        self.assertEqual(summary["cash_balance"], 1000.0)
        self.assertEqual(summary["total_deposits"], 1000.0)
        
    def test_multiple_deposits(self):
        self.acc.deposit(1000.0, "First deposit")
        self.acc.deposit(500.0, "Second deposit")
        summary = self.acc.get_account_summary()
        self.assertEqual(summary["cash_balance"], 1500.0)
        self.assertEqual(summary["total_deposits"], 1500.0)
        
    def test_deposit_invalid_amount_zero(self):
        with self.assertRaises(ValueError) as context:
            self.acc.deposit(0.0)
        self.assertEqual(str(context.exception), "Amount must be positive")
        
    def test_deposit_invalid_amount_negative(self):
        with self.assertRaises(ValueError) as context:
            self.acc.deposit(-100.0)
        self.assertEqual(str(context.exception), "Amount must be positive")
        
    def test_withdrawal_valid_amount(self):
        self.acc.deposit(1000.0)
        result = self.acc.withdraw(300.0, "Test withdrawal")
        self.assertTrue(result["success"])
        self.assertEqual(result["amount"], 300.0)
        summary = self.acc.get_account_summary()
        self.assertEqual(summary["cash_balance"], 700.0)
        self.assertEqual(summary["total_withdrawals"], 300.0)
        
    def test_withdrawal_insufficient_funds(self):
        self.acc.deposit(100.0)
        with self.assertRaises(ValueError) as context:
            self.acc.withdraw(200.0)
        self.assertEqual(str(context.exception), "Insufficient funds for withdrawal")
        
    def test_withdrawal_invalid_amount_zero(self):
        with self.assertRaises(ValueError) as context:
            self.acc.withdraw(0.0)
        self.assertEqual(str(context.exception), "Amount must be positive")
        
    def test_withdrawal_invalid_amount_negative(self):
        with self.assertRaises(ValueError) as context:
            self.acc.withdraw(-100.0)
        self.assertEqual(str(context.exception), "Amount must be positive")


class TestStockOperations(unittest.TestCase):
    def setUp(self):
        self.acc = Account("Test User", "test@example.com", 10000.0)
    
    def test_get_share_price_valid_symbol(self):
        price = self.acc.get_share_price("RELIANCE.NS")
        self.assertEqual(price, 2850.00)
        
    def test_get_share_price_bse_equivalent(self):
        ns_price = self.acc.get_share_price("RELIANCE.NS")
        bo_price = self.acc.get_share_price("RELIANCE.BO")
        self.assertEqual(ns_price, bo_price)
        
    def test_get_share_price_invalid_symbol(self):
        with self.assertRaises(ValueError) as context:
            self.acc.get_share_price("INVALID.SYMBOL")
        self.assertIn("Invalid or unsupported symbol", str(context.exception))
        
    def test_get_available_symbols(self):
        symbols = self.acc.get_available_symbols()
        self.assertIn("RELIANCE.NS", symbols)
        self.assertIn("RELIANCE.BO", symbols)
        self.assertIn("TCS.NS", symbols)
        self.assertIn("TCS.BO", symbols)
        self.assertGreater(len(symbols), 10)
        
    def test_buy_valid_order_sufficient_funds(self):
        result = self.acc.buy("RELIANCE.NS", 2, "Test buy")
        self.assertTrue(result["success"])
        self.assertEqual(result["symbol"], "RELIANCE.NS")
        self.assertEqual(result["quantity"], 2)
        self.assertEqual(result["price"], 2850.00)
        
        # Check that cash balance was reduced correctly
        # Gross amount: 2850 * 2 = 5700
        # Charges will be calculated based on BRATE, ERATE, GRATE, SDRATE
        # brk = 5700 * 0.001 = 5.7
        # exc = 5700 * 0.0001 = 0.57
        # gst = (5.7 + 0.57) * 0.18 = 1.1286
        # std = 5700 * 0.0001 = 0.57
        # total charges = 5.7 + 0.57 + 1.1286 + 0.57 = 7.9686 ≈ 7.97
        # net amount = 5700 + 7.97 = 5707.97
        expected_balance = 10000.0 - 5707.97  # Approximately 4292.03
        summary = self.acc.get_account_summary()
        self.assertAlmostEqual(summary["cash_balance"], expected_balance, places=2)
        
    def test_buy_invalid_quantity_type(self):
        with self.assertRaises(ValueError) as context:
            self.acc.buy("RELIANCE.NS", 2.5)
        self.assertEqual(str(context.exception), "Quantity must be a positive integer")
        
    def test_buy_invalid_quantity_negative(self):
        with self.assertRaises(ValueError) as context:
            self.acc.buy("RELIANCE.NS", -2)
        self.assertEqual(str(context.exception), "Quantity must be a positive integer")
        
    def test_buy_insufficient_funds(self):
        with self.assertRaises(ValueError) as context:
            # Trying to buy 100 shares of RELIANCE which would cost much more than our balance
            self.acc.buy("RELIANCE.NS", 100)
        self.assertEqual(str(context.exception), "Insufficient funds for purchase")
        
    def test_sell_valid_holding(self):
        # First buy some shares
        self.acc.buy("RELIANCE.NS", 5, "Buy for selling")
        
        # Then sell some of them
        result = self.acc.sell("RELIANCE.NS", 2, "Test sell")
        self.assertTrue(result["success"])
        self.assertEqual(result["symbol"], "RELIANCE.NS")
        self.assertEqual(result["quantity"], 2)
        
    def test_sell_insufficient_quantity(self):
        # Buy 2 shares
        self.acc.buy("RELIANCE.NS", 2, "Buy for selling")
        
        # Try to sell 5 shares
        with self.assertRaises(ValueError) as context:
            self.acc.sell("RELIANCE.NS", 5)
        self.assertEqual(str(context.exception), "Insufficient quantity for sale")
        
    def test_sell_nonexistent_holding(self):
        with self.assertRaises(ValueError) as context:
            self.acc.sell("TCS.NS", 1)
        self.assertIn("No holdings for symbol", str(context.exception))


class TestHoldingsAndPnL(unittest.TestCase):
    def setUp(self):
        self.acc = Account("Test User", "test@example.com", 20000.0)
        
    def test_holdings_after_buy(self):
        self.acc.buy("RELIANCE.NS", 3, "First buy")
        holdings = self.acc.get_holdings_report()
        self.assertEqual(len(holdings), 1)
        holding = holdings[0]
        self.assertEqual(holding["symbol"], "RELIANCE.NS")
        self.assertEqual(holding["quantity"], 3)
        self.assertEqual(holding["avg_buy_price"], 2850.00)
        
    def test_average_price_multiple_buys_same_stock(self):
        # First buy: 2 shares at 2850
        self.acc.buy("RELIANCE.NS", 2, "First buy")
        
        # Second buy: 1 share at 2850 (same price)
        self.acc.buy("RELIANCE.NS", 1, "Second buy")
        
        holdings = self.acc.get_holdings_report()
        self.assertEqual(len(holdings), 1)
        holding = holdings[0]
        self.assertEqual(holding["quantity"], 3)
        self.assertEqual(holding["avg_buy_price"], 2850.00)
        
    def test_holdings_after_sell_partial(self):
        # Buy 5 shares
        self.acc.buy("RELIANCE.NS", 5, "Buy 5 shares")
        
        # Sell 2 shares
        self.acc.sell("RELIANCE.NS", 2, "Sell 2 shares")
        
        holdings = self.acc.get_holdings_report()
        self.assertEqual(len(holdings), 1)
        holding = holdings[0]
        self.assertEqual(holding["quantity"], 3)
        self.assertEqual(holding["avg_buy_price"], 2850.00)
        
    def test_holdings_after_sell_all(self):
        # Buy 3 shares
        self.acc.buy("RELIANCE.NS", 3, "Buy 3 shares")
        
        # Sell all 3 shares
        self.acc.sell("RELIANCE.NS", 3, "Sell all shares")
        
        holdings = self.acc.get_holdings_report()
        self.assertEqual(len(holdings), 0)
        
    def test_realized_pnl_on_sale(self):
        # Buy 3 shares at 2850
        self.acc.buy("RELIANCE.NS", 3, "Buy at 2850")
        
        # Sell 2 shares at 2850 (same price, so no profit/loss except charges)
        result = self.acc.sell("RELIANCE.NS", 2, "Sell at same price")
        # The realized P&L should be close to zero since sold at same price (minus charges)
        self.assertAlmostEqual(result["realized_pl"], 0, places=0)
        
    def test_unrealized_pnl(self):
        # Buy 2 shares at 2850
        self.acc.buy("RELIANCE.NS", 2, "Buy at 2850")
        
        portfolio = self.acc.get_portfolio_summary()
        # Current price is still 2850, so unrealized P&L should be close to zero (minus charges)
        self.assertAlmostEqual(portfolio["total_unrealized_pl"], 0, places=0)


class TestReports(unittest.TestCase):
    def setUp(self):
        self.acc = Account("Test User", "test@example.com", 10000.0)
        
    def test_get_transaction_history(self):
        # Perform several transactions
        self.acc.deposit(5000.0, "Additional deposit")
        self.acc.buy("RELIANCE.NS", 1, "Buy 1 share")
        self.acc.sell("RELIANCE.NS", 1, "Sell 1 share")
        
        history = self.acc.get_transaction_history()
        self.assertEqual(len(history), 3)
        
        # Check transaction types
        types = [t["type"] for t in history]
        self.assertIn("DEPOSIT", types)
        self.assertIn("BUY", types)
        self.assertIn("SELL", types)
        
        # Check that each transaction has a timestamp
        for transaction in history:
            self.assertIsNotNone(transaction["timestamp"])
            self.assertNotEqual(transaction["timestamp"], "")
            
    def test_unique_transaction_ids(self):
        # Perform several transactions
        self.acc.deposit(1000.0)
        self.acc.buy("TCS.NS", 1)
        self.acc.sell("TCS.NS", 1)
        
        history = self.acc.get_transaction_history()
        ids = [t["transaction_id"] for t in history]
        
        # Check that all IDs are unique
        self.assertEqual(len(ids), len(set(ids)))
        
        # Check ID format
        for tx_id in ids:
            self.assertTrue(tx_id.startswith("TXN_"))
            
    def test_get_price_report(self):
        report = self.acc.get_price_report()
        self.assertGreater(len(report), 0)
        
        # Check that each entry has required fields
        for item in report:
            self.assertIn("symbol", item)
            self.assertIn("price", item)
            self.assertIn("exchange", item)
            self.assertIn(item["exchange"], ["NSE", "BSE"])
            
    def test_account_summary_structure(self):
        summary = self.acc.get_account_summary()
        
        # Check required fields exist
        required_fields = [
            "owner_name", "email", "cash_balance", "total_deposits",
            "total_withdrawals", "net_cash_invested", "total_portfolio_value",
            "total_holdings_value", "total_unrealized_pl", "total_realized_pl",
            "total_pl", "total_return_pct", "timestamp"
        ]
        
        for field in required_fields:
            self.assertIn(field, summary)
            
    def test_dashboard_data_structure(self):
        dashboard = self.acc.get_all_dashboard_data()
        
        # Check required sections exist
        self.assertIn("account_summary", dashboard)
        self.assertIn("portfolio_summary", dashboard)
        self.assertIn("holdings_report", dashboard)
        self.assertIn("transaction_history", dashboard)
        self.assertIn("price_report", dashboard)


class TestIntegrationScenarios(unittest.TestCase):
    def test_complete_trading_scenario(self):
        acc = Account("Trader", "trader@example.com", 50000.0)
        
        # Deposit more money
        acc.deposit(20000.0, "Monthly deposit")
        
        # Buy some stocks
        acc.buy("RELIANCE.NS", 5, "Buy Reliance")
        acc.buy("TCS.NS", 3, "Buy TCS")
        
        # Partially sell some stocks
        acc.sell("RELIANCE.NS", 2, "Sell some Reliance")
        
        # Check final state
        summary = acc.get_account_summary()
        self.assertEqual(summary["owner_name"], "Trader")
        self.assertEqual(summary["email"], "trader@example.com")
        
        holdings = acc.get_holdings_report()
        # Should have 3 Reliance and 3 TCS
        reliance_holding = next((h for h in holdings if h["symbol"] == "RELIANCE.NS"), None)
        tcs_holding = next((h for h in holdings if h["symbol"] == "TCS.NS"), None)
        
        self.assertIsNotNone(reliance_holding)
        self.assertEqual(reliance_holding["quantity"], 3)
        
        self.assertIsNotNone(tcs_holding)
        self.assertEqual(tcs_holding["quantity"], 3)
        
        # Check transaction history
        history = acc.get_transaction_history()
        self.assertEqual(len(history), 4)
        
        # All transactions should have timestamps
        for transaction in history:
            self.assertIsNotNone(transaction["timestamp"])
            self.assertNotEqual(transaction["timestamp"], "")


if __name__ == '__main__':
    unittest.main()