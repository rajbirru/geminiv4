import streamlit as st

def display_learn_tab(gemini_chat, user_profile_data):
    st.markdown("### Learn")
    
    # Generate a personalized learning prompt based on user profile and latest trends
    learning_prompt = f"""
    Given the following user profile:
    - Age: {user_profile_data['age']}
    - Retirement Age: {user_profile_data['retirement_age']}
    - Time Horizon: {user_profile_data['retirement_age'] - user_profile_data['age']} years
    - Income: {user_profile_data['income']}
    - Savings: {user_profile_data['savings']}
    - Investment Amount: {user_profile_data['investment_amount']}
    - Risk Tolerance: {user_profile_data['risk_tolerance']}
    - Investment Goals: {user_profile_data['investment_goals']}

    Provide personalized learning recommendations for this user based on their profile, the latest financial trends, and hot topics in the world of finance. Include a mix of beginner-friendly and more advanced resources, such as articles, blog posts, videos, podcasts, or courses. Ensure the content is fresh, appealing, timely, and specific to the user's needs and interests.

    For each recommendation, provide a brief description of why it's relevant and beneficial for the user, followed by a link to the resource. Aim for 3-5 recommendations in total.
    """

    # Get personalized learning recommendations from the LLM
    try:
        learn_response = gemini_chat.send_message(learning_prompt)
        learn_content = ''.join([chunk.text for chunk in learn_response])
    except Exception as e:
        st.error(f"Error getting learn content: {str(e)}")
        learn_content = "Error retrieving learn content."
    
    # Display the personalized learning recommendations
    st.markdown(learn_content)