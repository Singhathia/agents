#!/usr/bin/env python3
"""Account Management System for Trading Simulation Platform"""

from datetime import datetime
from typing import Dict, List, Any


# Module-level function for share price lookup
def get_share_price(symbol: str) -> float:
    """
    Returns the current price of a share.
    
    Test implementation returns fixed prices for AAPL, TSLA, GOOGL.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Current share price as float
        
    Raises:
        ValueError: If symbol is not in the test database
    """
    test_prices = {
        'AAPL': 150.00,
        'TSLA': 250.00,
        'GOOGL': 2800.00
    }
    
    if symbol not in test_prices:
        raise ValueError(f"Unknown symbol: {symbol}")
    
    return test_prices[symbol]


class Account:
    """
    Represents a user's trading account with balance management,
    transaction tracking, and portfolio calculation capabilities.
    """
    
    def __init__(self, account_id: str, initial_deposit: float = 0.0) -> None:
        """
        Initialize a new trading account.
        
        Args:
            account_id: Unique identifier for the account
            initial_deposit: Initial funds to deposit (default: 0.0)
            
        Raises:
            ValueError: If initial_deposit is negative
        """
        if initial_deposit < 0:
            raise ValueError("Initial deposit cannot be negative")
        
        self.account_id = account_id
        self.balance = 0.0
        self.holdings: Dict[str, int] = {}
        self.transactions: List[Dict[str, Any]] = []
        self.transaction_counter = 0
        self.total_deposited = 0.0
        self.total_withdrawn = 0.0
        
        # If initial deposit is provided, record it
        if initial_deposit > 0:
            self.deposit(initial_deposit)
    
    def _generate_transaction_id(self) -> int:
        """Generate unique transaction identifier."""
        self.transaction_counter += 1
        return self.transaction_counter
    
    def _record_transaction(self, transaction: Dict[str, Any]) -> None:
        """Store a transaction in the history."""
        transaction['timestamp'] = datetime.now()
        self.transactions.append(transaction)
    
    def _validate_symbol(self, symbol: str) -> None:
        """Validate that a stock symbol is recognized."""
        get_share_price(symbol)
    
    def deposit(self, amount: float) -> float:
        """
        Add funds to the account balance.
        
        Args:
            amount: The amount to deposit
            
        Returns:
            The new account balance after deposit
            
        Raises:
            ValueError: If amount is negative or zero
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        self.balance += amount
        self.total_deposited += amount
        
        transaction = {
            'transaction_id': self._generate_transaction_id(),
            'type': 'deposit',
            'symbol': None,
            'quantity': 0,
            'price': 0.0,
            'amount': amount,
            'balance_after': self.balance
        }
        self._record_transaction(transaction)
        
        return self.balance
    
    def withdraw(self, amount: float) -> float:
        """
        Remove funds from the account balance.
        
        Args:
            amount: The amount to withdraw
            
        Returns:
            The new account balance after withdrawal
            
        Raises:
            ValueError: If amount is negative, zero, or exceeds available balance
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        if amount > self.balance:
            raise ValueError("Insufficient funds for withdrawal")
        
        self.balance -= amount
        self.total_withdrawn += amount
        
        transaction = {
            'transaction_id': self._generate_transaction_id(),
            'type': 'withdraw',
            'symbol': None,
            'quantity': 0,
            'price': 0.0,
            'amount': amount,
            'balance_after': self.balance
        }
        self._record_transaction(transaction)
        
        return self.balance
    
    def buy_shares(self, symbol: str, quantity: int) -> float:
        """
        Purchase shares of a given stock.
        
        Args:
            symbol: Stock ticker symbol
            quantity: Number of shares to purchase
            
        Returns:
            The new account balance after purchase
            
        Raises:
            ValueError: If quantity is not positive, symbol is unknown, or insufficient funds
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        self._validate_symbol(symbol)
        
        price = get_share_price(symbol)
        total_cost = price * quantity
        
        if total_cost > self.balance:
            raise ValueError("Insufficient funds for purchase")
        
        self.balance -= total_cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        
        transaction = {
            'transaction_id': self._generate_transaction_id(),
            'type': 'buy',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'amount': total_cost,
            'balance_after': self.balance
        }
        self._record_transaction(transaction)
        
        return self.balance
    
    def sell_shares(self, symbol: str, quantity: int) -> float:
        """
        Sell shares of a given stock.
        
        Args:
            symbol: Stock ticker symbol
            quantity: Number of shares to sell
            
        Returns:
            The new account balance after sale
            
        Raises:
            ValueError: If quantity is not positive, symbol is unknown, or insufficient shares
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        self._validate_symbol(symbol)
        
        current_holdings = self.holdings.get(symbol, 0)
        if quantity > current_holdings:
            raise ValueError(f"Insufficient shares. You own {current_holdings} shares of {symbol}")
        
        price = get_share_price(symbol)
        total_proceeds = price * quantity
        
        self.balance += total_proceeds
        self.holdings[symbol] -= quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
        
        transaction = {
            'transaction_id': self._generate_transaction_id(),
            'type': 'sell',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'amount': total_proceeds,
            'balance_after': self.balance
        }
        self._record_transaction(transaction)
        
        return self.balance
    
    def get_balance(self) -> float:
        """
        Retrieve the current cash balance.
        
        Returns:
            Current available cash balance
        """
        return self.balance
    
    def get_holdings(self) -> Dict[str, int]:
        """
        Retrieve current stock holdings.
        
        Returns:
            Dictionary mapping stock symbols to share quantities owned
        """
        return dict(self.holdings)
    
    def get_portfolio_value(self) -> float:
        """
        Calculate total portfolio value including cash and holdings.
        
        Returns:
            Total portfolio value (cash + current value of all holdings)
        """
        holdings_value = 0.0
        for symbol, quantity in self.holdings.items():
            price = get_share_price(symbol)
            holdings_value += price * quantity
        
        return self.balance + holdings_value
    
    def get_profit_loss(self) -> float:
        """
        Calculate total profit or loss from initial deposit.
        
        Returns:
            Profit (positive) or loss (negative) from initial deposit
        """
        total_invested = self.total_deposited - self.total_withdrawn
        return self.get_portfolio_value() - total_invested
    
    def get_total_deposited(self) -> float:
        """
        Get total amount deposited into the account.
        
        Returns:
            Sum of all deposit transactions
        """
        return self.total_deposited
    
    def get_total_withdrawn(self) -> float:
        """
        Get total amount withdrawn from the account.
        
        Returns:
            Sum of all withdrawal transactions
        """
        return self.total_withdrawn
    
    def get_transactions(self) -> List[Dict[str, Any]]:
        """
        Retrieve complete transaction history.
        
        Returns:
            List of transaction records in chronological order
        """
        return [dict(t) for t in self.transactions]
    
    def get_account_summary(self) -> Dict[str, Any]:
        """
        Retrieve a comprehensive account summary.
        
        Returns:
            Dictionary containing account overview
        """
        return {
            'account_id': self.account_id,
            'balance': self.balance,
            'portfolio_value': self.get_portfolio_value(),
            'total_value': self.get_portfolio_value(),
            'profit_loss': self.get_profit_loss(),
            'holdings': self.get_holdings(),
            'total_deposited': self.total_deposited,
            'total_withdrawn': self.total_withdrawn,
            'transaction_count': len(self.transactions)
        }
