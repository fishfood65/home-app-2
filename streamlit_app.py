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
st.write("Let's gather some information. Please enter your details:")

# Get user Input to enter input
city = st.text_input("Enter Your City:")
zip_code = st.text_input("Enter Your Zip Code:")

# Save the user input for later use
user_info = {"city": city, "zip_code": zip_code}

# Display a button and perform an action based on user input
if st.button("Click to Accept Level 1: Trainee Mission"):
    st.write(f"You entered: {city}, {zip_code}. We'll provide personalized utilities informaion for your area.")

# Read user_info to get city and zip_code
city = user_info["city"]
zip_code = user_info["zip_code"]

# Generate the AI prompt
api_key = os.getenv("MISTRAL_TOKEN")

if not api_key:
    api_key = st.text_input("Enter your Mistral API key:", type="password")

if api_key:
    st.success("API key successfully loaded.")
else:
   st.error("API key is not set.")

   # Display environment variables in the Streamlit app
#st.title("Environment Variables")

# Display all environment variables
#env_vars = "\n".join([f"{key}: {value}" for key, value in os.environ.items()])
#st.text(env_vars)

with st.expander("AI Prompt Preview"):
    user_confirmation = st.checkbox("Show AI Prompt")
    if user_confirmation:
        prompt = f"""
            Generate a comprehensive list of utility providers, excluding cable and internet services, for the specified city and zip code, along with descriptions, names, contact numbers, addresses, and websites.
            City: {city}, Zip Code: {zip_code}
            
            Electricity:

            - Provider Name: <electricity_provider_name>
            - Description: <electricity_provider_description>
            - Address: <electricity_provider_address>
            - Contact Number: <electricity_provider_phone>
            - Website: <electricity_provider_website>

            Natural Gas:

            - Provider Name: <natural_gas_provider_name>
            - Description: <natural_gas_provider_description>
            - Address: <natural_gas_provider_address>
            - Contact Number: <natural_gas_provider_phone>
            - Website: <natural_gas_provider_website>
            
            Water:
            - Provider Name: <water_provider_name>
            - Description: <water_provider_description>
            - Address: <water_provider_address>
            - Contact Number: <water_provider_phone>
            - Website: <water_provider_website>
            
            Sewer:

            - Provider Name: <sewer_provider_name>
            - Description: <sewer_provider_description>
            - Address: <sewer_provider_address>
            - Contact Number: <sewer_provider_phone>
            - Website: <sewer_provider_website>
            
            Garbage/Recycling:

            - Provider Name: <garbage_recycling_provider_name>
            - Description: <garbage_recycling_provider_description>
            - Address: <garbage_recycling_provider_address>
            - Contact Number: <garbage_recycling_provider_phone>
            - Website: <garbage_recycling_provider_website>
            
            Please replace <city>, <zip_code>, and placeholders like <electricity_provider_name>, <electricity_provider_description>, etc., with the actual information for the specified city and zip code. This prompt will generate a detailed list of utility providers, excluding cable and internet services, along with the requested information.
            """
        st.code(prompt)

# Generate comprehensive output using Hugging Face API
st.subheader("Complete Level 1: Trainee Mission")
st.write ("Click the button to generate your persoanlized utlities contacts document")

# Function to process the output for formatting (e.g., apply bold, italics, headings)
def process_output_for_formatting(output):
    # Example processing: bold headings or text wrapped in markdown-style asterisks
    formatted_text = ""
    # Replace markdown-like headings (e.g., ## Heading) with docx headings
    formatted_text = re.sub(r"^## (.*)", r"\n\n\1\n", output)
    
    # Replace markdown-like bold (e.g., **bold**)
    formatted_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", formatted_text)
    
    # Replace markdown-like italics (e.g., *italic*)
    formatted_text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", formatted_text)
    
    return formatted_text

if st.button("Complete Mission"):
    if user_confirmation:
        # Use Mistral for model inference
        client = Mistral(api_key=api_key)
        
        # Define the prompt as a "chat" message format
        completion = client.chat.complete(
            model="open-mistral-nemo",  # Specify the model ID
            messages=[  # Pass a message format similar to a conversation
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,  # Set the max tokens
            temperature=0.5,  # Control the randomness of the output
        )
        
        # Access the content from the 'AssistantMessage' object using the .content attribute
        output = completion.choices[0].message.content # Access the generated message
        
        # Convert `output` to string if it's not already a string
        if isinstance(output, str):
            output_text = output
        else:
            # If output is an object, extract its string representation
            output_text = str(output)  # You can also try accessing specific attributes if needed
        
        st.success("Utilities contacts generated successfully! Mission Accomplished.")
        st.write(output_text)

        # Create a DOCX file from the output text
        doc = Document()
        doc.add_heading('Home Utilities Contact Info', 0)
        
        # Process and add formatted output to the document
        # Example: preserve line breaks and formatting in output
        formatted_output = process_output_for_formatting(output)
        doc.add_paragraph(formatted_output)
    

        # Save DOCX to a temporary file
        doc_filename = "home_utilities_contacts.docx"
        doc.save(doc_filename)

        # Provide a download button for the DOCX file
        with open(doc_filename, "rb") as doc_file:
            st.download_button(
                label="Download Runbook as DOCX",
                data=doc_file,
                file_name=doc_filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    else:
        st.warning("Please confirm the AI prompt before generating the runbook.")
