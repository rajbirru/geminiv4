# few_shot_template.py

few_shot_template = """
Here are a few examples of personalized portfolio recommendations based on the user's profile and investment goals. Each recommendation includes a table with asset class allocations (Stocks, ETFs, Funds, Bonds, CDs, Cash) and a list of specific investments with their respective percentages.

Example 1:
User Profile: Age 35, Retirement Age 65, Time Horizon 30 years, Income $60,000, Savings $20,000, Risk Tolerance High, Investment Goal: Retirement
Recommendation:
Asset Class Allocation:
| Asset Class | Allocation |
| ----------- | ---------- |
| Stocks      | 70%        |
| Bonds       | 20%        |
| Alternative Investments | 10% |

Specific Investments (based on a $20,000 investment):
- VOO (Vanguard S&P 500 ETF): 35% ($7,000)
- QQQ (Invesco QQQ ETF): 20% ($4,000)
- VXUS (Vanguard Total International Stock ETF): 15% ($3,000)
- BND (Vanguard Total Bond Market ETF): 15% ($3,000)
- REIT (Vanguard Real Estate ETF): 5% ($1,000)
- GLD (SPDR Gold Shares): 5% ($1,000)
- Cash: 5% ($1,000)

Total: 100% ($20,000)

Rebalance annually.

Example 2:
User Profile: Age 55, Retirement Age 65, Time Horizon 10 years, Income $80,000, Savings $300,000, Risk Tolerance Low, Investment Goal: Retirement
Recommendation:
Asset Class Allocation:
| Asset Class | Allocation |
| ----------- | ---------- |
| Stocks      | 40%        |
| Bonds       | 50%        |
| Cash        | 10%        |

Specific Investments (based on a $300,000 investment):
- VYM (Vanguard High Dividend Yield ETF): 20% ($60,000)
- SCHD (Schwab U.S. Dividend Equity ETF): 10% ($30,000)
- VTI (Vanguard Total Stock Market ETF): 10% ($30,000)
- BIV (Vanguard Intermediate-Term Bond ETF): 25% ($75,000)
- VCIT (Vanguard Intermediate-Term Corporate Bond ETF): 15% ($45,000)
- VGIT (Vanguard Intermediate-Term Treasury ETF): 10% ($30,000)
- Cash: 10% ($30,000)

Total: 100% ($300,000)

Rebalance every 2-3 years.

Your task: Based on the provided User Profile, User Message, and the total investment amount, generate a personalized portfolio recommendation with an asset class allocation table and a list of specific investments with their respective percentages and dollar amounts. Ensure that the total allocation adds up to 100%.
"""