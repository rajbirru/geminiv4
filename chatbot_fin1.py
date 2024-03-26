import streamlit as st
import google.generativeai as genai
from system_context import get_system_context
from user_profile import UserProfile
import re
from portfolio_utils import extract_portfolio_items, display_portfolio_chart
import random
import time
from few_shot_template import few_shot_template
from market_sentiment import get_market_sentiment
from learn import display_learn_tab
from financial_wisdom import show_random_finance_wisdom
from market_news import generate_financial_news_prompt
import plotly.graph_objects as go

def display_portfolio_chart(portfolio_items):
    if portfolio_items and all(portfolio_items.values()):
        labels = list(portfolio_items.keys())
        values = [len(items) for items in portfolio_items.values()]
        total_items = sum(values)
        percentages = [round(value / total_items * 100, 2) for value in values]

        fig = go.Figure(data=[go.Pie(labels=labels, values=percentages, hole=0.5, textinfo='label+percent')])
        fig.update_layout(title_text="Portfolio Allocation", title_x=0.5)

        st.plotly_chart(fig)

def display_market_news_tab(chat_instance):
    st.markdown("### Market News")

    try:
        news_prompt = generate_financial_news_prompt()
        news_response = chat_instance.send_message(news_prompt)
        news_content = ''.join([chunk.text for chunk in news_response])
    except Exception as e:
        st.error(f"Error getting market news: {str(e)}")
        news_content = "Error retrieving market news."

    st.markdown(news_content)

def suggest_portfolio(system_context, user_profile_summary, user_message, few_shot_template, investment_amount):
    prompt = f"""
    {system_context}

    {few_shot_template}

    User Profile:
    {user_profile_summary}

    User Message:
    {user_message}

    Total Investment Amount: ${investment_amount:,.2f}

    Response:
    """

    try:
        response = st.session_state.gemini_chat.send_message(prompt)
        portfolio_recommendation = ''.join([chunk.text for chunk in response])
        return portfolio_recommendation
    except google.api_core.exceptions.DeadlineExceeded:
        return "The request timed out due to the GenAI API limitations. Please try again later or consider simplifying your request."
    except Exception as e:
        return f"An error occurred while getting the LLM response: {str(e)}"

# Access your GOOGLE_API_KEY
google_api_key = st.secrets["GOOGLE_API_KEY"]
try:
    genai.configure(api_key=google_api_key)
except Exception as e:
    st.error(f"Error configuring Google AI: {str(e)}")
    st.stop()

def init_gemini_model():
    try:
        model = genai.GenerativeModel('gemini-pro')
        system_context = get_system_context()
        chat = model.start_chat()
        chat.send_message(system_context)
        return chat
    except Exception as e:
        st.error(f"Error initializing Gemini LLM: {str(e)}")
        st.stop()

if 'gemini_chat' not in st.session_state:
    st.session_state.gemini_chat = init_gemini_model()

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'user_profile' not in st.session_state:
    st.session_state.user_profile = UserProfile()

if 'default_user_input' not in st.session_state:
    st.session_state.default_user_input = "Build a portfolio of Stocks, ETFs, Funds, Bonds, Bond funds, CDs and any cash equivalents"

if 'user_profile_data' not in st.session_state:
    st.session_state.user_profile_data = {
        'investment_goals': 'Retirement',
        'age': 39,
        'retirement_age': 64,
        'income': 50000,
        'savings': 10000,
        'investment_amount': 10000,
        'risk_tolerance': 'Low'
    }

tab1, tab2, tab3, tab4 = st.tabs(["Advice", "Market Sentiment", "Learn", "News"])

with tab1:
    st.title("FinanceGPT")
    st.subheader("Your Personal Finance Assistant")

    with st.expander("Build Your Profile"):
        col1, col2 = st.columns(2)
        with col1:
            investment_goals = st.text_input("Enter your investment goals", value=st.session_state.user_profile_data['investment_goals'], key="investment_goals")
            age = st.slider("Your Age", min_value=18, max_value=100, value=st.session_state.user_profile_data['age'])
            retirement_age = st.slider("Your Desired Retirement Age", min_value=18, max_value=100, value=st.session_state.user_profile_data['retirement_age'])
            investment_amount = st.number_input("Amount Available for Investment", min_value=0, value=st.session_state.user_profile_data['investment_amount'], step=1000)
            time_horizon = retirement_age - age
            st.write(f"Investment Time Horizon: {time_horizon} years")
        with col2:
            income = st.number_input("Enter your annual income", min_value=0, value=st.session_state.user_profile_data['income'], step=1000)
            savings = st.number_input("Enter your total savings", min_value=0, value=st.session_state.user_profile_data['savings'], step=1000)
            risk_tolerance = st.selectbox("Select your risk tolerance", ("Low", "Medium", "High"), index=["Low", "Medium", "High"].index(st.session_state.user_profile_data['risk_tolerance']))

        if st.button("Update Profile"):
            st.session_state.user_profile_data = {
                'investment_goals': investment_goals,
                'age': age,
                'retirement_age': retirement_age,
                'income': income,
                'savings': savings,
                'investment_amount': investment_amount,
                'risk_tolerance': risk_tolerance
            }
            st.session_state.user_profile.update_profile(
                st.session_state.user_profile_data['age'],
                st.session_state.user_profile_data['retirement_age'],
                st.session_state.user_profile_data['retirement_age'] - st.session_state.user_profile_data['age'],
                st.session_state.user_profile_data['income'],
                st.session_state.user_profile_data['savings'],
                st.session_state.user_profile_data['investment_amount'],
                st.session_state.user_profile_data['risk_tolerance'],
                st.session_state.user_profile_data['investment_goals']
            )

    for message in st.session_state.messages:
        if message['role'] == 'user':
            st.write(f"User: {message['content']}")
        else:
            st.write(f"Assistant: {message['content']}")

    user_input = st.text_input("Type your message here...", value=st.session_state.default_user_input, key="user_input")

    if st.button("Submit", key="submit_button"):
        st.session_state.messages.append({'role': 'user', 'content': user_input})

        user_profile_summary = st.session_state.user_profile.get_profile_summary()
        system_context = get_system_context()
        investment_amount = st.session_state.user_profile_data['investment_amount']

        llm_response = suggest_portfolio(system_context, user_profile_summary, user_input, few_shot_template, investment_amount)

        st.session_state.messages.append({'role': 'assistant', 'content': llm_response})

        portfolio_items = extract_portfolio_items(llm_response)
        display_portfolio_chart(portfolio_items)

    quote = show_random_finance_wisdom()
    if quote:
        st.markdown(quote)

with tab2:
    sentiment, sentiment_color, market_sentiment = get_market_sentiment(st.session_state.gemini_chat)

    st.markdown("### Market Sentiment")
    st.markdown(f'<div style="color: {sentiment_color};">{sentiment}</div>', unsafe_allow_html=True)
    st.markdown(market_sentiment)

with tab3:
    display_learn_tab(st.session_state.gemini_chat, st.session_state.user_profile_data)

with tab4:
    display_market_news_tab(st.session_state.gemini_chat)

def extract_portfolio_items(response):
    portfolio_items = {
        "Stocks": [],
        "ETFs": [],
        "Funds": [],
        "Bonds": []
    }

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