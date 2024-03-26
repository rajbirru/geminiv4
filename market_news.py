import datetime

def generate_financial_news_prompt():
    today = datetime.date.today().strftime("%B %d, %Y")
    prompt = f"""
Given your comprehensive training on a diverse range of texts, including financial news articles, create a detailed overview of the latest and most significant financial news stories as of {today}.

Focus on pivotal economic trends, key stock market updates, and major financial industry events that could be shaping the global economy. For each story, provide:

1. A compelling headline that captures the essence of the news.
2. A concise summary that outlines the key points and their implications for the financial industry.
3. The likely global impact of these events on markets and economies.

Remember to draw upon your extensive database of economic indicators, market analysis, geopolitical factors, and historical events that have influenced the financial markets. Your response should reflect the depth of analysis found in expert financial commentary and embody the knowledge of economic cycles, investment strategies, and market sentiment.

Please ensure that the news stories you cover are current and relevant to the provided date ({today}).
"""
    return prompt