import re
import plotly.express as px

def extract_portfolio_items(response):
    portfolio_items = {
        "Stocks": [],
        "ETFs": [],
        "Funds": [],
        "Bonds": []
    }

    # Use regular expressions to extract tickers/symbols from the response
    stock_regex = r"(\b[A-Z]+\b)"
    etf_regex = r"(\b[A-Z]+\b(?= ETF))"
    fund_regex = r"(\b[A-Z]+\b(?= Fund))"
    bond_regex = r"(\b[A-Z]+\b(?= Bond))"

    stocks = re.findall(stock_regex, response, re.IGNORECASE)
    etfs = re.findall(etf_regex, response, re.IGNORECASE)
    funds = re.findall(fund_regex, response, re.IGNORECASE)
    bonds = re.findall(bond_regex, response, re.IGNORECASE)

    portfolio_items["Stocks"] = stocks
    portfolio_items["ETFs"] = etfs
    portfolio_items["Funds"] = funds
    portfolio_items["Bonds"] = bonds

    return portfolio_items

def display_portfolio_chart(portfolio_items):
    # Prepare the data for the chart
    labels = list(portfolio_items.keys())
    values = [len(items) for items in portfolio_items.values()]

    # Create a pie chart
    fig = px.pie(values=values, names=labels, title="Portfolio Allocation")

    # Display the chart in Streamlit
    return fig