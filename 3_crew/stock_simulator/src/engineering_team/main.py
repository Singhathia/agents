#!/usr/bin/env python
import sys
import warnings
import os

from engineering_team.crew import EngineeringTeam

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

os.makedirs("output", exist_ok=True)

module_name = "accounts"
module_file = "accounts.py"
class_name = "Account"


project_summary = f"""
Build a self-contained Indian stock market trading simulation and portfolio management system.

This is a learning/demo project, not real trading.

Final generated files:
1. output/{module_file}
2. output/app.py
3. output/test_{module_name}.py
4. output/{module_name}_design.md
5. output/validation_report.md

Important import rule:
- The backend module file is {module_file}
- The importable module name is {module_name}
- The main class name is {class_name}
- Correct import: from {module_name} import {class_name}
- Incorrect import: from {module_name}.py import {class_name}

The project must use Process.sequential and memory=False.
"""


backend_requirements = f"""
Backend file:
- Generate one complete Python backend module named {module_file}.
- The file must expose one main class named {class_name}.
- The module must be importable using: from {module_name} import {class_name}
- Use only Python standard library.
- Do not use internet access, external APIs, databases, pandas, numpy, or paid services.
- Use INR as the currency.
- Keep the backend compact and reliable.
- Target approximately 250 to 420 lines.
- Do not include UI code.
- Do not include demo code under if __name__ == "__main__".
- The file must pass: python -m py_compile {module_file}

Indian stock market simulation:
- Support deterministic fixed stock prices.
- Support NSE/BSE-style symbols such as:
  RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, ICICIBANK.NS,
  SBIN.NS, ITC.NS, TATAMOTORS.NS, ADANIENT.NS, WIPRO.NS.
- Also support .BO equivalents for the same base symbols.
- Normalize symbols to uppercase.
- Validate simple Indian market symbol format SYMBOL.NS or SYMBOL.BO.
- Quantities must be positive integers.
- Money inputs must be positive numbers.

Suggested fixed NSE prices:
- RELIANCE.NS: 2850.00
- TCS.NS: 3900.00
- INFY.NS: 1500.00
- HDFCBANK.NS: 1650.00
- ICICIBANK.NS: 1100.00
- SBIN.NS: 750.00
- ITC.NS: 430.00
- TATAMOTORS.NS: 950.00
- ADANIENT.NS: 3200.00
- WIPRO.NS: 500.00

For .BO equivalents, use the same price as the .NS version unless otherwise needed.

Strict public API contract:
The {class_name} class must provide these public methods:

- __init__(owner_name: str = "Demo User", email: str | None = None, initial_deposit: float = 0.0)
- deposit(amount: float, notes: str = "") -> dict
- withdraw(amount: float, notes: str = "") -> dict
- buy(symbol: str, quantity: int, notes: str = "") -> dict
- sell(symbol: str, quantity: int, notes: str = "") -> dict
- get_share_price(symbol: str) -> float
- get_available_symbols() -> list[str]
- get_price_report() -> list[dict]
- get_account_summary() -> dict
- get_portfolio_summary() -> dict
- get_holdings_report() -> list[dict]
- get_transaction_history() -> list[dict]
- get_profit_loss_report() -> dict
- get_all_dashboard_data() -> dict

Required behavior:
- Allow account creation with owner name, optional email, and optional initial deposit.
- Track cash balance.
- Track total deposits.
- Track total withdrawals.
- Track net cash invested.
- Prevent negative cash balance.
- Prevent invalid deposits and withdrawals.
- Prevent buying if cash is insufficient.
- Prevent selling more shares than owned.
- Track holdings per symbol.
- Track quantity owned.
- Track average buy price.
- Track total invested per holding.
- Track realized P&L after sells.
- Track unrealized P&L using fixed prices.
- Track current market value.
- Calculate total portfolio value as cash balance + holdings market value.
- Calculate total P&L as total portfolio value - net cash invested.
- Calculate total return percentage.
- Record every transaction.

Transaction fields:
- transaction_id
- timestamp
- type
- symbol
- exchange
- quantity
- price
- gross_amount
- charges
- net_amount
- notes

Timestamp guidance:
- Transactions may use current datetime.
- Tests should not depend on the exact timestamp.
- Timestamp should be returned as a non-empty ISO-style string.

Trading charges:
- Use simple deterministic simulated charges.
- Charges do not need to be legally exact.
- Include brokerage, exchange charge, GST-style charge, and stamp-duty-style charge.
- Keep rates configurable inside the class.
- Clearly separate gross trade value, charges, and final cash impact.

Report output:
- All reports must return plain dictionaries or lists of dictionaries.
- Round currency values to 2 decimal places.
- Reports should be frontend-friendly.
- Do not return custom objects from report methods.
"""


frontend_requirements = f"""
Frontend file:
- Generate one complete Gradio app named app.py.
- The app must import the backend using: from {module_name} import {class_name}
- Assume app.py and {module_file} are in the same output directory.
- The app must run with: python app.py
- The app must pass: python -m py_compile app.py
- The app must end exactly with:

if __name__ == "__main__":
    demo.launch()

Frontend scope:
- Build a compact but polished Gradio Blocks app.
- Use one demo account instance.
- Use only the public API methods from the backend.
- Keep the app compact and reliable.
- Target approximately 180 to 320 lines.
- Do not use pandas.
- Do not use Plotly.
- Do not use internet calls.
- Do not use external market data.
- Avoid large CSS blocks.
- Avoid complex duplicated callbacks.
- Use one shared refresh_dashboard() helper.

Required Gradio components:
- Blocks
- Tabs or grouped sections
- Markdown metric cards
- Textbox
- Number
- Dropdown
- Button
- Dataframe
- Plot

Required UI sections:
1. Account Setup
2. Deposit / Withdraw
3. Buy / Sell Stocks
4. Portfolio Dashboard
5. Holdings
6. Transactions
7. Profit & Loss

Dashboard metrics:
- Cash Balance
- Portfolio Market Value
- Total Portfolio Value
- Net Cash Invested
- Total P&L
- Total Return %
- Realized P&L
- Unrealized P&L

Tables:
- Holdings table from get_holdings_report()
- Transaction table from get_transaction_history()
- Price table from get_price_report()

Charts in v1:
- Include exactly 2 lightweight charts.
- Use matplotlib only.
- Do not use pandas or Plotly.
- If matplotlib import fails, the app should still compile and run by returning None for charts.
- Chart 1: portfolio allocation by holding.
- Chart 2: cash vs holdings market value OR realized vs unrealized P&L.
- Keep chart helpers short.

Callback structure:
- setup_account callback
- deposit callback
- withdraw callback
- buy callback
- sell callback
- refresh_dashboard helper
- refresh button callback

Completion rules:
- Do not stop inside a list, dictionary, callback, function, with-block, or component definition.
- Every .click() call must have complete inputs and outputs.
- All brackets, parentheses, and strings must be closed.
- Output only raw Python code.
"""


test_requirements = f"""
Test file:
- Generate one complete test file named test_{module_name}.py.
- The test file must import using: from {module_name} import {class_name}
- Prefer unittest from the Python standard library.
- Do not require pytest unless absolutely necessary.
- Tests must be deterministic.
- Tests must not use internet access.
- Tests must not require real market prices.
- Tests must not depend on the exact current timestamp.
- Tests should pass when run from the output directory.

Tests should cover:
- account creation
- initial deposit
- deposit behavior
- withdrawal behavior
- failed withdrawal when cash is insufficient
- invalid deposit and withdrawal amounts
- Indian stock symbol normalization
- invalid stock symbol handling
- get_share_price for known Indian stocks
- get_available_symbols
- get_price_report
- buy order success
- buy order failure due to insufficient cash
- sell order success
- sell order failure due to insufficient holdings
- holdings quantity after buys and sells
- average buy price after multiple buys
- realized P&L after selling
- unrealized P&L using fixed prices
- portfolio market value
- total account/portfolio value
- total return percentage
- transaction history structure
- holdings report structure
- account summary report structure
- profit/loss report structure
- dashboard data structure
- transaction IDs are unique
- timestamp field exists and is non-empty

The test file must pass:
python -m py_compile test_{module_name}.py
"""


validation_requirements = f"""
Validation rules:
- Validate generated Python files immediately after each code-generation task.
- If a generated file passes validation, output the complete original file unchanged.
- If a generated file fails validation, rewrite the complete affected file compactly.
- Do not output patches.
- Do not output explanations when the validation task writes a Python file.
- Do not output markdown when the validation task writes a Python file.
- Validation tasks that write Python files must output raw Python code only.

Backend validation must verify:
- output/{module_file} compiles.
- from {module_name} import {class_name} works from the output directory.
- {class_name} exposes the required public methods.

Frontend validation must verify:
- output/app.py compiles.
- app.py imports from {module_name} correctly.
- app.py ends with the launch guard.
- app.py includes exactly 2 lightweight chart outputs or chart helper functions.
- app.py does not use pandas or Plotly.

Test validation must verify:
- output/test_{module_name}.py compiles.
- it imports from {module_name} correctly.
- tests are deterministic.
- tests do not assert exact timestamps.

Final validation must verify:
- output/{module_file} compiles.
- output/app.py compiles.
- output/test_{module_name}.py compiles.
- backend import works.
- tests can be run if the environment supports it.
"""


def run():
    inputs = {
        "project_summary": project_summary,
        "backend_requirements": backend_requirements,
        "frontend_requirements": frontend_requirements,
        "test_requirements": test_requirements,
        "validation_requirements": validation_requirements,
        "module_name": module_name,
        "module_file": module_file,
        "class_name": class_name,
    }

    EngineeringTeam().crew().kickoff(inputs=inputs)


if __name__ == "__main__":
    run()