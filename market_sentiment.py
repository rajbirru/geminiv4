import streamlit as st
import re

def get_market_sentiment(gemini_chat):
    # Get market sentiment from the LLM
    market_sentiment_prompt = "Provide a brief overview of the current market sentiment, including any notable trends, all-time highs, bullish or bearish sentiment, and any indications of the current stage of the business cycle. Clearly state whether the overall sentiment is bullish, bearish, or mixed."
    try:
        market_sentiment_response = gemini_chat.send_message(market_sentiment_prompt)
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
    elif "mixed" in market_sentiment.lower():
        sentiment_color = "neutral"

    # Extract the sentiment from the market_sentiment
    sentiment_match = re.search(r'Current Market Sentiment: (.*)', market_sentiment, re.IGNORECASE)
    if sentiment_match:
        sentiment = sentiment_match.group(1)
        market_sentiment = market_sentiment.replace(sentiment_match.group(0), "").strip()
    else:
        sentiment = "Sentiment Unclear"

    return sentiment, sentiment_color, market_sentiment