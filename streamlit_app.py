import streamlit as st
from mistralai import Mistral
import os
import pandas as pd
from datetime import datetime, timedelta
from docx import Document
import re

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

api_key = os.getenv("MISTRAL_TOKEN")

if not api_key:
    api_key = st.text_input("Enter your Mistral API key:", type="password")

if api_key:
    st.success("API key successfully loaded.")
else:
   st.error("API key is not set.")

   # Display environment variables in the Streamlit app
st.title("Environment Variables")

# Display all environment variables
env_vars = "\n".join([f"{key}: {value}" for key, value in os.environ.items()])
st.text(env_vars)

