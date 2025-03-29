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
    city_zip = st.text_input("Enter Your City and Zip Code:")
    st.write(f"Thank you for entering {city_zip}. We'll provide tailored emergency instructions for your area.")

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
#st.title("Environment Variables")

# Display all environment variables
#env_vars = "\n".join([f"{key}: {value}" for key, value in os.environ.items()])
#st.text(env_vars)

# Section for date range selection
st.subheader("Choose Date(s) or Timeframe")
st.write ("Choose a Timeframe you would like a runbook generated for.")

# Define the options
options = ["Pick Dates", "Weekdays Only", "Weekend Only", "Default"]

# Create a radio selection
choice = st.radio("Choose an option:", options)

if choice == "Pick Dates":
    start_date = st.date_input("Select Start Date:", datetime.now())
    end_date = st.date_input("Select End Date:", datetime.now() + timedelta(days=7))
    st.write(f"You selected specific dates from {start_date} to {end_date}.")
elif choice == "Weekdays Only":
    st.write("You selected weekdays only.")
elif choice == "Weekend Only":
    st.write("You selected weekend only.")
elif choice == "Default":
    st.write("You selected a general schedule.")
else:
    st.write("Invalid choice.")

# Generate AI prompt and get user confirmation
with st.expander("AI Prompt Preview"):
    user_confirmation = st.checkbox("Show AI Prompt")
    if user_confirmation:
        if choice == "Pick Dates":
            prompt = f"""
            Generate a comprehensive pet sitting runbook for the selected date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}.
            
            User Inputs:
            {uploaded_files}
            
            System Input(from PDF):
            {system_info}
            
            Instructions:
            - Create a detailed runbook tailored to the user's pets for the specified dates.
            - Include sections for basic information, health, feeding, grooming, daily routine, and emergency contacts.
            - Adapt the runbook based on the number and types of pets provided.
            
            Output Format:
            - Use a clear structure with headings for each pet.
            - Provide a schedule, feeding instructions, and individual care routines for the selected dates.
            
            Example User Input:
            - Pet 1:
              - Name: Fluffy
              - Type: Cat
              - ...
            
            Example System Input:
            [System input content]
            
            Example Output:
            [Provide an example runbook section for the selected dates here]
            """
        elif choice == "Weekdays Only":
            prompt = f"""
            Generate a comprehensive pet sitting runbook for weekdays only.
            
            User Inputs:
            {uploaded_files}
            
            System Input(from PDF):
            {system_info}
            
            Instructions:
            - Create a detailed runbook tailored to the user's pets for weekdays.
            - Include sections for basic information, health, feeding, grooming, and emergency contacts.
            - Adapt the runbook based on the number and types of pets.
            
            Output Format:
            - Use a clear structure with headings for each pet.
            - Provide a weekly schedule, feeding instructions, and individual care routines for weekdays.
            
            Example User Input:
            - Pet 1:
              - Name: Fluffy
              - Type: Cat
              - ...
            
            Example System Input:
            [System input content]
            
            Example Output:
            [Provide an example runbook section for weekdays here]
            """
        elif choice == "Weekend Only":
            prompt = f"""
            Generate a comprehensive pet sitting runbook for the weekend only.
            
            User Inputs:
            {uploaded_files}
            
            System Input(from PDF):
            {system_info}
            
            Instructions:
            - Create a detailed runbook tailored to the user's pets for the weekend.
            - Include sections for basic information, health, feeding, grooming, and emergency contacts.
            - Adapt the runbook based on the number and types of pets.
            
            Output Format:
            - Use a clear structure with headings for each pet.
            - Provide a schedule for the weekend, focusing on pet care tasks.
            
            Example User Input:
            - Pet 1:
              - Name: Fluffy
              - Type: Cat
              - ...
            
            Example System Input:
            [System input content]
            
            Example Output:
            [Provide an example runbook section for the weekend here]
            """
        else:
            prompt = f"""
            Generate a comprehensive pet sitting runbook based on the following user and system inputs:
            
            User Inputs:
            {uploaded_files}
            
            System Input(from PDF):
            {system_info}
            
            Instructions:
            - Create a detailed runbook tailored to the user's pets.
            - Include sections for basic information, health, feeding, grooming, daily routine, and emergency contacts.
            - Adapt the runbook based on the number and types of pets provided.
            
            Output Format:
            - Use a clear structure with headings for each pet.
            - Provide a weekly schedule, feeding instructions, and individual care routines.
            
            Example User Input:
            - Pet 1:
              - Name: Fluffy
              - Type: Cat
              - ...
            
            Example System Input:
            [System input content]
            
            Example Output:
            [Provide an example runbook section here]
            """
        st.code(prompt)

# Generate comprehensive output using Hugging Face API
st.subheader("Runbook Creation")
st.write ("Click the button to generate your persoanlized Runbook")

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

if st.button("Generate Runbook"):
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
        
        st.success("Runbook generated successfully!")
        st.write(output_text)

        # Create a DOCX file from the output text
        doc = Document()
        doc.add_heading('Pet Sitting Runbook', 0)
        
        # Process and add formatted output to the document
        # Example: preserve line breaks and formatting in output
        formatted_output = process_output_for_formatting(output)
        doc.add_paragraph(formatted_output)
    

        # Save DOCX to a temporary file
        doc_filename = "runbook.docx"
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
