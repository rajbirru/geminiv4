import streamlit as st
import random

# A dictionary of financial experts and their quotes
finance_quotes = {
    "Benjamin Graham": [
        "The intelligent investor is a realist who sells to optimists and buys from pessimists.",
        "In the short run, the market is a voting machine, but in the long run, it is a weighing machine."
        # ... Add more quotes here
    ],
    "John Bogle": [
        "The mutual fund industry has been built, in a sense, on witchcraft.",
        "Time is your friend; impulse is your enemy."
        # ... Add more quotes here
    ],
    "Peter Lynch": [
        "Know what you own, and know why you own it.",
        "The best stock to buy may be the one you already own."
        # ... Add more quotes here
    ],
    # ... Add more experts and their quotes here
}

def show_random_finance_wisdom():
    # Select a random finance expert
    expert = random.choice(list(finance_quotes.keys()))
    # Select a random quote from that expert's list of quotes
    quote = random.choice(finance_quotes[expert])
    # Display the quote and the expert's name
    st.markdown(f"> \"{quote}\" - {expert}")

# Somewhere in your Streamlit layout
st.markdown("### Wisdom from Financial Experts")
show_random_finance_wisdom()
