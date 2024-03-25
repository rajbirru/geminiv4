import streamlit as st
import google.generativeai as genai
from system_context import get_system_context
from user_profile import UserProfile
import re
from portfolio_utils import extract_portfolio_items, display_portfolio_chart
import random

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

# Initialize loading state
if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False

# Initialize default user input
if 'default_user_input' not in st.session_state:
    st.session_state.default_user_input = "Build a portfolio of Stocks, ETFs, Funds, Bonds, Bond funds, CDs and any cash equivalents"

# Initialize user profile data in session state
if 'user_profile_data' not in st.session_state:
    st.session_state.user_profile_data = {
        'investment_goals': 'Retirement',
        'age': 39,
        'retirement_age': 64,
        'income': 50000,
        'savings': 10000,
        'risk_tolerance': 'Low'
    }

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
        investment_goals = st.text_input("Enter your investment goals", value=st.session_state.user_profile_data['investment_goals'],
                                         on_change=lambda: update_user_profile('investment_goals', investment_goals))
        age = st.slider("Your Age", min_value=18, max_value=100, value=st.session_state.user_profile_data['age'],
                        on_change=lambda: update_user_profile('age', age))
        retirement_age = st.slider("Your Desired Retirement Age", min_value=18, max_value=100, value=st.session_state.user_profile_data['retirement_age'],
                                   on_change=lambda: update_user_profile('retirement_age', retirement_age))
        time_horizon = retirement_age - age
        st.write(f"Investment Time Horizon: {time_horizon} years")
        income = st.number_input("Enter your annual income", min_value=0, value=st.session_state.user_profile_data['income'], step=1000,
                                 on_change=lambda: update_user_profile('income', income))
        savings = st.number_input("Enter your total savings", min_value=0, value=st.session_state.user_profile_data['savings'], step=1000,
                                  on_change=lambda: update_user_profile('savings', savings))
        risk_tolerance = st.selectbox("Select your risk tolerance", ("Low", "Medium", "High"), index=["Low", "Medium", "High"].index(st.session_state.user_profile_data['risk_tolerance']),
                                      on_change=lambda: update_user_profile('risk_tolerance', risk_tolerance))

    def update_user_profile(key, value):
        st.session_state.user_profile_data[key] = value
        st.session_state.user_profile.update_profile(
            st.session_state.user_profile_data['age'],
            st.session_state.user_profile_data['retirement_age'],
            st.session_state.user_profile_data['retirement_age'] - st.session_state.user_profile_data['age'],
            st.session_state.user_profile_data['income'],
            st.session_state.user_profile_data['savings'],
            st.session_state.user_profile_data['risk_tolerance'],
            st.session_state.user_profile_data['investment_goals']
        )

    # Display messages from the chat history
    for message in st.session_state.messages:
        message_class = "user-message" if message['role'] == 'user' else "assistant-message"
        st.markdown(f'<div class="chat-message {message_class}">{message["content"]}</div>', unsafe_allow_html=True)

    # Input for the user's message
    user_input = st.text_input("Type your message here...", value=st.session_state.default_user_input, key="user_input")

    if st.button("Submit", key="submit_button"):
        if not st.session_state.is_loading:
            st.session_state.is_loading = True
            
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
            finally:
                st.session_state.is_loading = False

            # Process the LLM response and update the chat history
            st.session_state.messages.append({'role': 'assistant', 'content': llm_response})

            # Extract the selected stocks, ETFs, funds, and bonds from the LLM response
            portfolio_items = extract_portfolio_items(llm_response)

    # Display loading message while processing
    if st.session_state.is_loading:
        st.markdown('<div class="loading-message">Processing your request...</div>', unsafe_allow_html=True)
    else:
        # Display messages from the chat history
        for message in st.session_state.messages:
            message_class = "user-message" if message['role'] == 'user' else "assistant-message"
            st.markdown(f'<div class="chat-message {message_class}">{message["content"]}</div>', unsafe_allow_html=True)

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
    
    # Define the few-shot prompt with random link selection
    few_shot_prompt = """
Generate educational summaries for the following financial topics, providing useful blogs and videos for each. Each summary should briefly explain the topic and why it's important, followed by links to further reading or viewing.

1. **Topic: Understanding Stocks**
Understanding stocks is crucial for anyone looking to invest in the stock market. Stocks represent ownership in a company and can provide significant returns over time. For beginners, grasping the basics of how stocks work is the first step toward successful investing.
Blogs and Videos:
- [Basics of What Stocks Are](https://www.investopedia.com/terms/s/stock.asp)
- [Investing in Stocks: How to Start for Beginners](https://www.youtube.com/watch?v=ARrNYyJEnFI)
- [How to Read Stock Charts](https://www.nerdwallet.com/article/investing/how-to-read-stock-charts)

2. **Topic: Financial Planning for Future Security**
Financial planning is essential for securing a comfortable future. It involves setting financial goals, budgeting, saving, investing, and managing debt. Effective financial planning can help individuals achieve their long-term goals, such as retirement or buying a home.
Blogs and Videos:
- [A Beginner's Guide to Financial Planning](https://www.forbes.com/advisor/financial-planning/financial-planning-where-to-start/)
- [Financial Planning: A Comprehensive Guide](https://www.youtube.com/watch?v=0A5c8hFqIgU)
- [Steps for Successful Financial Planning](https://www.nerdwallet.com/blog/investing/financial-planning-steps/)

3. **Topic: Overcoming Common Financial Worries**
Many individuals face common financial worries, such as debt, saving for retirement, and emergency funds. Understanding how to manage these concerns is key to financial well-being.
Blogs and Videos:
- [Managing Debt: Strategies and Tips](https://www.creditkarma.com/advice/i/how-to-get-out-of-debt)
- [Saving for Retirement: Basics and Tips](https://www.youtube.com/watch?v=1C8Qlh5HCJ8)
- [How to Build an Emergency Fund](https://www.bankrate.com/banking/savings/building-an-emergency-fund/)

Please follow the above format to generate educational summaries for these topics, ensuring the information is clear, concise, and beneficial for individuals looking to improve their financial literacy.


Example 3:
Topic: {new_finance_topic}
Blogs and Videos:
-
-
-
"""
    
    # Get a new finance topic and related resources from the LLM
    try:
        learn_response = st.session_state.gemini_chat.send_message(few_shot_prompt)
        learn_content = ''.join([chunk.text for chunk in learn_response])
    except Exception as e:
        st.error(f"Error getting learn content: {str(e)}")
        learn_content = "Error retrieving learn content."
    
    # Display the LLM-generated learn content
    st.markdown(learn_content)
    
    # Display additional static resources
    st.write("Check out these additional resources to enhance your financial knowledge:")
    resources = [
        "[Investopedia](https://www.investopedia.com/)",
        "[The Motley Fool](https://www.fool.com/)",
        "[MarketWatch](https://www.marketwatch.com/)",
        "[Graham Stephan YouTube Channel](https://www.youtube.com/c/GrahamStephan)",
        "[Andrei Jikh YouTube Channel](https://www.youtube.com/c/AndreiJikh)"
    ]
    random.shuffle(resources)
    for resource in resources:
        st.markdown(f"- {resource}")


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
    st.plotly_chart(fig)