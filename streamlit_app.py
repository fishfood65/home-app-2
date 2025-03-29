import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to Home Hero Academy! 👋")

st.sidebar.success("Select a demo above.")


st.markdown(
    """
    ### Your Mission
    Accept a series of challenges testing your knowledge about your home to empower you and your deputies to become a heroic guardian for your home and its precious contents
"""
)

st.markdown(
    """
    ### Start your Training!
"""
)
# Display a button for the user to accept the mission
if st.button("Accept Mission"):
    st.write("You've accepted the mission! Let's get started. Please enter your city and zip code:")
    city = st.text_input("Enter Your City and Zip Code:")
    st.write(f"Thank you for entering {city}. We'll provide tailored emergency instructions for your area.")

# If the user doesn't accept the mission, display a message
else:
    st.write("You haven't accepted the mission yet. Please click the button to begin your journey.")
