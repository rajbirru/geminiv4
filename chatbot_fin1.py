import streamlit as st
import google.generativeai as genai
from system_context import get_system_context
from user_profile import UserProfile
import matplotlib.pyplot as plt
import plotly.express as px
import re
from portfolio_utils import extract_portfolio_items, display_portfolio_chart

# Set page title and favicon
st.set_page_config(page_title="FinanceGPT", page_icon=":money_with_wings:")

# Apply modern styling
st.markdown(
    """
    <style>
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #f5f5f5;
    }
    .title {
        font-size: 36px;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 20px;
    }
    .subtitle {
        font-size: 24px;
        color: #2c3e50;
        margin-bottom: 30px;
    }
    .chat-message {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .user-message {
        background-color: #e6f7ff;
    }
    .assistant-message {
        background-color: #f0f8ff;
    }
    .bearish {
        color: #FF0000;
        font-weight: bold;
    }
    .bullish {
        color: #00FF00;
        font-weight: bold;
    }
    .neutral {
        color: #FFA500;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Access your GOOGLE_API_KEY
google_api_key = st.secrets["GOOGLE_API_KEY"]
try:
    genai.configure(api_key=google_api_key)
except Exception as e:
    st.error(f"Error configuring Google AI: {str(e)}")
    st.stop()

# Function to initialize the Gemini LLM model and start a chat session
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

# Initialize the chat session
if 'gemini_chat' not in st.session_state:
    st.session_state.gemini_chat = init_gemini_model()

# Initialize message history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Initialize user profile
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = UserProfile()

# Create tabs
tab1, tab2, tab3 = st.tabs(["Advice", "Market Sentiment", "Learn"])

with tab1:
    # Title and subtitle
    st.markdown('<div class="title">FinanceGPT</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Your Personal Finance Assistant</div>', unsafe_allow_html=True)

    # Initialize portfolio_items
    portfolio_items = {}

    # User profile input
    with st.expander("Build Your Profile"):
        investment_goals = st.text_input("Enter your investment goals", value="Retirement")
        age = st.slider("Your Age", min_value=18, max_value=100, value=30)
        retirement_age = st.slider("Your Desired Retirement Age", min_value=18, max_value=100, value=60)
        time_horizon = retirement_age - age
        st.write(f"Investment Time Horizon: {time_horizon} years")
        income = st.number_input("Enter your annual income", min_value=0, value=50000, step=1000)
        savings = st.number_input("Enter your total savings", min_value=0, value=10000, step=1000)
        risk_tolerance = st.selectbox("Select your risk tolerance", ("Low", "Medium", "High"))

        if st.button("Save Profile"):
            st.session_state.user_profile.update_profile(age, retirement_age, time_horizon, income, savings, risk_tolerance, investment_goals)

    # Display messages from the chat history
    for message in st.session_state.messages:
        message_class = "user-message" if message['role'] == 'user' else "assistant-message"
        st.markdown(f'<div class="chat-message {message_class}">{message["content"]}</div>', unsafe_allow_html=True)

    # Input for the user's message
    default_user_input = "Build me a portfolio of stocks, ETFs, Bonds and funds"
    user_input = st.text_input("Type your message here...", value=default_user_input, key="user_input")

if st.button("Submit"):
    # Append user message to chat history
    st.session_state.messages.append({'role': 'user', 'content': user_input})

    # Initialize llm_response
    llm_response = ""

    # Send the user input along with the user profile and market sentiment to the LLM and fetch the response
    user_profile_summary = st.session_state.user_profile.get_profile_summary()
    system_context = get_system_context()
    try:
        response = st.session_state.gemini_chat.send_message(f"{system_context}\n\nUser Profile:\n{user_profile_summary}\n\nUser Message:\n{user_input}")
        llm_response = ''.join([chunk.text for chunk in response])
    except Exception as e:
        st.error(f"Error getting LLM response: {str(e)}")
        llm_response = "Error generating portfolio recommendation."

    # Process the LLM response and update the chat history
    st.session_state.messages.append({'role': 'assistant', 'content': llm_response})

    # Extract the selected stocks, ETFs, funds, and bonds from the LLM response
    portfolio_items = extract_portfolio_items(llm_response)

    # # Display the portfolio chart
    # if portfolio_items:
    #     fig = display_portfolio_chart(portfolio_items)
    #     st.plotly_chart(fig)
    # else:
    #     st.warning("No portfolio items found in the recommendation.")

with tab2:
    # Get market sentiment from the LLM
    market_sentiment_prompt = "Provide a brief overview of the current market sentiment, including any notable trends, all-time highs, bullish or bearish sentiment, and any indications of the current stage of the business cycle."
    try:
        market_sentiment_response = st.session_state.gemini_chat.send_message(market_sentiment_prompt)
        market_sentiment = ''.join([chunk.text for chunk in market_sentiment_response])
    except Exception as e:
        st.error(f"Error getting market sentiment: {str(e)}")
        market_sentiment = "Error retrieving market sentiment."

    # Determine sentiment color based on keywords
    sentiment_color = "neutral"
    if "bearish" in market_sentiment.lower():
        sentiment_color = "bearish"
    elif "bullish" in market_sentiment.lower():
        sentiment_color = "bullish"

    # Display market sentiment with color coding
    st.markdown("### Market Sentiment")
    st.markdown(f'<div class="{sentiment_color}">{market_sentiment}</div>', unsafe_allow_html=True)

with tab3:
    st.markdown("### Learn")
    st.write("Check out these prominent blogs and YouTube videos to enhance your financial knowledge:")
    st.markdown("- [Investopedia](https://www.investopedia.com/)")
    st.markdown("- [The Motley Fool](https://www.fool.com/)")
    st.markdown("- [MarketWatch](https://www.marketwatch.com/)")
    st.markdown("- [Graham Stephan YouTube Channel](https://www.youtube.com/c/GrahamStephan)")
    st.markdown("- [Andrei Jikh YouTube Channel](https://www.youtube.com/c/AndreiJikh)")



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

    # # Create a pie chart
    # fig = px.pie(values=values, names=labels, title="Portfolio Allocation")

    # # Display the chart in Streamlit
    # st.plotly_chart(fig)