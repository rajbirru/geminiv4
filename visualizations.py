import plotly.graph_objects as go
import streamlit as st

def display_portfolio_chart(portfolio_items):
    # Prepare the data for the chart
    labels = list(portfolio_items.keys())
    values = [len(items) for items in portfolio_items.values()]

    # Create a donut chart
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5)])
    fig.update_layout(title_text="Portfolio Allocation", title_x=0.5)

    # Display the chart in Streamlit
    st.plotly_chart(fig)