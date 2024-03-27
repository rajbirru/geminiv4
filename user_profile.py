class UserProfile:
    def __init__(self):
        self.age = None
        self.retirement_age = None
        self.time_horizon = None
        self.income = None
        self.savings = None
        self.investment_amount = None
        self.risk_tolerance = None
        self.investment_goals = None

    def update_profile(self, age, retirement_age, time_horizon, income, savings, investment_amount, risk_tolerance, investment_goals):
        self.age = age
        self.retirement_age = retirement_age
        self.time_horizon = time_horizon
        self.income = income
        self.savings = savings
        self.investment_amount = investment_amount
        self.risk_tolerance = risk_tolerance
        self.investment_goals = investment_goals

    def get_profile_summary(self):
        profile_summary = f"Age: {self.age}\n"
        profile_summary += f"Desired Retirement Age: {self.retirement_age}\n"
        profile_summary += f"Investment Time Horizon: {self.time_horizon} years\n"
        profile_summary += f"Income: {self.income}\n"
        profile_summary += f"Savings: {self.savings}\n"
        profile_summary += f"Investment Amount: {self.investment_amount}\n"
        profile_summary += f"Risk Tolerance: {self.risk_tolerance}\n"
        profile_summary += f"Investment Goals: {self.investment_goals}"
        return profile_summary