import google.generativeai as genai

# Configuration (Consider loading these from a secure source)
genai.configure(api_key="YOUR_API_KEY")
DEFAULT_BASE_MODEL = "gemini-ultra-1.0"
DEFAULT_GENERATION_CONFIG = {
    "temperature": 0.6,  # Some creativity for portfolio ideas
    "top_p": 1,
    "max_output_tokens": 512  
}

class FinancialAnalystLLM:
    def __init__(self, base_model=DEFAULT_BASE_MODEL, generation_config=DEFAULT_GENERATION_CONFIG):
        self.base_model = base_model
        self.generation_config = generation_config
        self.system_context = self.build_system_context()

    def build_system_context(self):
        return """
        You are a financial analyst AI assistant. Provide portfolio recommendations aligned with the user's profile. Consider asset classes like stocks, bonds, and ETFs.  Focus on diversification and risk management.

        **Important:**
        * Do not give specific ticker symbols or exact percentages.  
        * Emphasize consulting a financial advisor before investments.
        * Prioritize reliable resources and avoid highly speculative assets.
        """

    def generate_portfolio_ideas(self, user_profile):
        few_shot_prompt = self.build_few_shot_prompt(user_profile)  # We'll define this next
        task = "Create several model portfolio suggestions tailored to this user profile. Include a brief rationale for each."

        response = genai.generate(
            model=self.base_model,
            prompt=self.system_context + few_shot_prompt + "\n" + task + "\n",
            **self.generation_config
        )
        return response.text.strip() 

    def build_few_shot_prompt(self, user_profile):
        return f"""
        ### User Profile
        * Age: {user_profile['age']}
        * Time Horizon: {user_profile['time_horizon']}
        * Amount to Invest: {user_profile['amount_to_invest']}
        * Investment Goal: {user_profile['investment_goal']}
        * Risk Profile: {user_profile['risk_profile']} 
        """

# Example Usage (For testing)
if __name__ == "__main__":
    user_profile = {
        "age": 35,
        "time_horizon": "10+ years",
        "amount_to_invest": "$50,000",
        "investment_goal": "Retirement",
        "risk_profile": "Moderate" 
    }

    analyst = FinancialAnalystLLM()
    response = analyst.generate_portfolio_ideas(user_profile)
    print(response)
