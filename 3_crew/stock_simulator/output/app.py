import gradio as gr
from accounts import Account

# Initialize demo account
demo_account = Account("Demo Trader", "demo@example.com")

def setup_account(name, email, deposit):
    global demo_account
    try:
        demo_account = Account(name, email, deposit)
        return f"Account created for {name} with ₹{deposit:.2f} deposit."
    except Exception as e:
        return f"Error creating account: {str(e)}"

# Helper to create portfolio allocation chart
def plot_allocation_chart():
    try:
        import matplotlib.pyplot as plt
        holdings = demo_account.get_holdings_report()
        if not holdings:
            return None
            
        symbols = [h["symbol"].replace(".NS", "").replace(".BO", "") for h in holdings]
        values = [h["current_value"] for h in holdings]
        
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(values, labels=symbols, autopct='%1.1f%%')
        ax.set_title("Portfolio Allocation by Value")
        plt.tight_layout()
        return fig
    except:
        return None

# Helper to create cash vs holdings chart
def plot_cash_vs_holdings_chart():
    try:
        import matplotlib.pyplot as plt
        summary = demo_account.get_portfolio_summary()
        cash = summary["cash_balance"]
        holdings = summary["total_holdings_value"]
        
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(["Cash", "Holdings"], [cash, holdings], color=["green", "blue"])
        ax.set_ylabel("Value (₹)")
        ax.set_title("Cash vs Holdings Market Value")
        plt.tight_layout()
        return fig
    except:
        return None

# Refresh dashboard data
def refresh_dashboard():
    data = demo_account.get_all_dashboard_data()
    summary = data["account_summary"]
    portfolio = data["portfolio_summary"]
    
    # Format metrics as markdown cards
    cash_card = f"## ₹{summary['cash_balance']:,.2f}\n**Cash Balance**"
    market_card = f"## ₹{portfolio['total_holdings_value']:,.2f}\n**Holdings Market Value**"
    total_card = f"## ₹{summary['total_portfolio_value']:,.2f}\n**Total Portfolio Value**"
    invested_card = f"## ₹{summary['net_cash_invested']:,.2f}\n**Net Cash Invested**"
    pnl_card = f"## ₹{portfolio['total_pl']:,.2f}\n**Total P&L**"
    return_card = f"## {portfolio['total_return_pct']:+.2f}%\n**Return %**"
    realized_card = f"## ₹{portfolio['total_realized_pl']:,.2f}\n**Realized P&L**"
    unrealized_card = f"## ₹{portfolio['total_unrealized_pl']:,.2f}\n**Unrealized P&L**"
    
    holdings_df = data["holdings_report"]
    transactions_df = data["transaction_history"]
    prices_df = data["price_report"]
    
    return (
        cash_card, market_card, total_card, invested_card,
        pnl_card, return_card, realized_card, unrealized_card,
        holdings_df, transactions_df, prices_df,
        plot_allocation_chart(), plot_cash_vs_holdings_chart()
    )

# Transaction functions
def deposit_funds(amount, notes):
    try:
        result = demo_account.deposit(amount, notes)
        return result["message"], *refresh_dashboard()
    except Exception as e:
        return f"Error: {str(e)}", *refresh_dashboard()

def withdraw_funds(amount, notes):
    try:
        result = demo_account.withdraw(amount, notes)
        return result["message"], *refresh_dashboard()
    except Exception as e:
        return f"Error: {str(e)}", *refresh_dashboard()

def buy_stock(symbol, qty, notes):
    try:
        result = demo_account.buy(symbol, qty, notes)
        return result["message"], *refresh_dashboard()
    except Exception as e:
        return f"Error: {str(e)}", *refresh_dashboard()

def sell_stock(symbol, qty, notes):
    try:
        result = demo_account.sell(symbol, qty, notes)
        return result["message"], *refresh_dashboard()
    except Exception as e:
        return f"Error: {str(e)}", *refresh_dashboard()

with gr.Blocks(title="Indian Stock Trading Simulator") as demo:
    gr.Markdown("# 🇮🇳 Indian Stock Trading Simulator")
    
    with gr.Tab("Account Setup"):
        with gr.Row():
            with gr.Column():
                name_input = gr.Textbox(label="Owner Name", value="Demo Trader")
                email_input = gr.Textbox(label="Email (optional)", value="demo@example.com")
                deposit_input = gr.Number(label="Initial Deposit (₹)", value=100000)
                setup_btn = gr.Button("Create Account")
                setup_output = gr.Textbox(label="Status")
                setup_btn.click(
                    setup_account,
                    inputs=[name_input, email_input, deposit_input],
                    outputs=setup_output
                )
    
    with gr.Tab("Portfolio Dashboard"):
        with gr.Row():
            refresh_btn = gr.Button("Refresh Dashboard")
        
        with gr.Row():
            cash_metric = gr.Markdown()
            market_metric = gr.Markdown()
            total_metric = gr.Markdown()
            invested_metric = gr.Markdown()
            
        with gr.Row():
            pnl_metric = gr.Markdown()
            return_metric = gr.Markdown()
            realized_metric = gr.Markdown()
            unrealized_metric = gr.Markdown()
        
        with gr.Row():
            allocation_plot = gr.Plot()
            cash_plot = gr.Plot()
    
    with gr.Tab("Transactions"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Deposit Funds")
                dep_amount = gr.Number(label="Amount (₹)")
                dep_notes = gr.Textbox(label="Notes")
                dep_btn = gr.Button("Deposit")
                
                gr.Markdown("### Withdraw Funds")
                wd_amount = gr.Number(label="Amount (₹)")
                wd_notes = gr.Textbox(label="Notes")
                wd_btn = gr.Button("Withdraw")
                
            with gr.Column():
                gr.Markdown("### Buy Stock")
                buy_symbol = gr.Dropdown(choices=demo_account.get_available_symbols(), label="Symbol")
                buy_qty = gr.Number(label="Quantity", minimum=1, step=1)
                buy_notes = gr.Textbox(label="Notes")
                buy_btn = gr.Button("Buy")
                
                gr.Markdown("### Sell Stock")
                sell_symbol = gr.Dropdown(choices=demo_account.get_available_symbols(), label="Symbol")
                sell_qty = gr.Number(label="Quantity", minimum=1, step=1)
                sell_notes = gr.Textbox(label="Notes")
                sell_btn = gr.Button("Sell")
        
        transaction_status = gr.Textbox(label="Transaction Status")
        
        dep_btn.click(
            deposit_funds,
            inputs=[dep_amount, dep_notes],
            outputs=[transaction_status, cash_metric, market_metric, total_metric, invested_metric,
                     pnl_metric, return_metric, realized_metric, unrealized_metric,
                     gr.Dataframe(), gr.Dataframe(), gr.Dataframe(), allocation_plot, cash_plot]
        )
        
        wd_btn.click(
            withdraw_funds,
            inputs=[wd_amount, wd_notes],
            outputs=[transaction_status, cash_metric, market_metric, total_metric, invested_metric,
                     pnl_metric, return_metric, realized_metric, unrealized_metric,
                     gr.Dataframe(), gr.Dataframe(), gr.Dataframe(), allocation_plot, cash_plot]
        )
        
        buy_btn.click(
            buy_stock,
            inputs=[buy_symbol, buy_qty, buy_notes],
            outputs=[transaction_status, cash_metric, market_metric, total_metric, invested_metric,
                     pnl_metric, return_metric, realized_metric, unrealized_metric,
                     gr.Dataframe(), gr.Dataframe(), gr.Dataframe(), allocation_plot, cash_plot]
        )
        
        sell_btn.click(
            sell_stock,
            inputs=[sell_symbol, sell_qty, sell_notes],
            outputs=[transaction_status, cash_metric, market_metric, total_metric, invested_metric,
                     pnl_metric, return_metric, realized_metric, unrealized_metric,
                     gr.Dataframe(), gr.Dataframe(), gr.Dataframe(), allocation_plot, cash_plot]
        )
    
    with gr.Tab("Holdings"):
        holdings_table = gr.Dataframe(label="Current Holdings")
    
    with gr.Tab("Transaction History"):
        transactions_table = gr.Dataframe(label="Recent Transactions")
    
    with gr.Tab("Stock Prices"):
        prices_table = gr.Dataframe(label="Current Prices")
    
    refresh_btn.click(
        refresh_dashboard,
        inputs=[],
        outputs=[
            cash_metric, market_metric, total_metric, invested_metric,
            pnl_metric, return_metric, realized_metric, unrealized_metric,
            holdings_table, transactions_table, prices_table,
            allocation_plot, cash_plot
        ]
    )
    
    # Initialize dashboard on load
    demo.load(
        refresh_dashboard,
        inputs=[],
        outputs=[
            cash_metric, market_metric, total_metric, invested_metric,
            pnl_metric, return_metric, realized_metric, unrealized_metric,
            holdings_table, transactions_table, prices_table,
            allocation_plot, cash_plot
        ]
    )

if __name__ == "__main__":
    demo.launch()