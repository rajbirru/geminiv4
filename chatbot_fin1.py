import streamlit as st
import google.generativeai as genai
from system_context import get_system_context
from user_profile import UserProfile
from few_shot_template import few_shot_template
from market_sentiment import get_market_sentiment
from learn import display_learn_tab
from financial_wisdom import show_random_finance_wisdom
from market_news import generate_financial_news_prompt

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
    except Exception as e:
        return f"An error occurred while getting the LLM response: {str(e)}"

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
        'investment_amount': 10000,
        'risk_tolerance': 'Low'
    }

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Advice", "Market Sentiment", "Learn", "News"])

with tab1:
    # Title and subtitle
    st.title("FinanceGPT")
    st.subheader("Your Personal Finance Assistant")

    # User profile input
    with st.expander("Build Your Profile"):
        investment_goals = st.text_input("Enter your investment goals", value=st.session_state.user_profile_data['investment_goals'])
        age = st.slider("Your Age", min_value=18, max_value=100, value=st.session_state.user_profile_data['age'])
        retirement_age = st.slider("Your Desired Retirement Age", min_value=18, max_value=100, value=st.session_state.user_profile_data['retirement_age'])
        investment_amount = st.number_input("Amount Available for Investment", min_value=0, value=st.session_state.user_profile_data['investment_amount'], step=1000)
        time_horizon = retirement_age - age
        st.write(f"Investment Time Horizon: {time_horizon} years")
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

    # Display messages from the chat history
    for message in st.session_state.messages:
        if message['role'] == 'user':
            st.write(f"User: {message['content']}")
        else:
            st.write(f"Assistant: {message['content']}")

    # Input for the user's message
    user_input = st.text_input("Type your message here...", value=st.session_state.default_user_input, key="user_input")

    if st.button("Submit", key="submit_button"):
        # Append user message to chat history
        st.session_state.messages.append({'role': 'user', 'content': user_input})

        # Initialize llm_response
        llm_response = ""

        # Get the user profile summary, system context, few-shot template, and investment amount
        user_profile_summary = st.session_state.user_profile.get_profile_summary()
        system_context = get_system_context()
        investment_amount = st.session_state.user_profile_data['investment_amount']

        llm_response = suggest_portfolio(system_context, user_profile_summary, user_input, few_shot_template, investment_amount)

        # Process the LLM response and update the chat history
        st.session_state.messages.append({'role': 'assistant', 'content': llm_response})

    # Display messages from the chat history
    for message in st.session_state.messages:
        if message['role'] == 'user':
            st.write(f"User: {message['content']}")
        else:
            st.write(f"Assistant: {message['content']}")

    # Display a random quote from a financial expert at the bottom
    quote = show_random_finance_wisdom()
    if quote:
        st.markdown(quote)

with tab2:
    sentiment, sentiment_color, market_sentiment = get_market_sentiment(st.session_state.gemini_chat)

    # Display market sentiment with color coding
    st.markdown("### Market Sentiment")
    st.markdown(f'<div><span style="color: {sentiment_color};">{sentiment}</span></div>', unsafe_allow_html=True)
    st.markdown(market_sentiment)

with tab3:
    display_learn_tab(st.session_state.gemini_chat, st.session_state.user_profile_data)

with tab4:
    st.markdown("### Latest Market News")
    news_prompt = generate_financial_news_prompt()
    news_response = st.session_state.gemini_chat.send_message(news_prompt)
    news_content = ''.join([chunk.text for chunk in news_response])
    st.markdown(news_content)