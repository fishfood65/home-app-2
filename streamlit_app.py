import streamlit as st
import re
from mistralai import Mistral, UserMessage
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime, timedelta
from docx import Document
import re
import time
from PIL import Image
import io

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
# Generate the AI prompt
api_key = os.getenv("MISTRAL_TOKEN")
client = Mistral(api_key=api_key)

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

# Main entry point of the app
def main():
# Define available levels
    levels = ("Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Bonus Level")

# Initialize session state with default section if not already set
    if "section" not in st.session_state:
        st.session_state.section = levels[0]

# Sidebar radio button with session state support
    st.session_state.section = st.sidebar.radio(
    "Choose a Level:",
        levels,
        index=levels.index(st.session_state.section)
    )

# Display the selected section
    #st.write(f"### You selected: {st.session_state.section}")

# Conditional content rendering
    if st.session_state.section == "Level 1":
        st.subheader("🏁 Welcome to Level 1")
    # Add Level 1 content here
        home()

    elif st.session_state.section == "Level 2":
        st.subheader("🔧 Level 2 Tools")
    # Add Level 2 content here

    elif st.session_state.section == "Level 3":
        st.subheader("📊 Level 3 Data")
    # Add Level 3 content here

    elif st.session_state.section == "Level 4":
        st.subheader("🧠 Level 4 Analysis")
    # Add Level 4 content here

    elif st.session_state.section == "Level 5":
        st.subheader("🚀 Level 5 Launch")
    # Add Level 5 content here

    elif st.session_state.section == "Bonus Level":
        st.subheader("🎁 Bonus Level Content")
    # Add Bonus Level content here

#### Reusable Functions to Generate and Format Runbooks #####

def generate_runbook_from_prompt(
    prompt: str,
    api_key: str,
    button_text: str = "Generate Runbook",
    doc_heading: str = "Emergency Runbook",
    doc_filename: str = "runbook.docx"
):
    """
    Reusable Streamlit function to handle LLM completion and export a DOCX file.

    Args:
        prompt (str): The input prompt for Mistral.
        api_key (str): Your Mistral API key.
        button_text (str): Label for the Streamlit button.
        doc_heading (str): Heading used in the generated DOCX.
        doc_filename (str): Name of the DOCX file for download.
    """
    if st.button(button_text):
        # Optional user confirmation from session_state or UI
        if st.session_state.get("user_confirmation", True):  # default to True if not set
            try:
                client = Mistral(api_key=api_key)

                completion = client.chat.complete(
                    model="mistral-small-latest",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1500,
                    temperature=0.5,
                )

                output = completion.choices[0].message.content
                output_text = output if isinstance(output, str) else str(output)

                st.success(f"{doc_heading} generated successfully!")
                st.write(output_text)

                # Format and write to DOCX
                doc = Document()
                doc.add_heading(doc_heading, 0)
                formatted_output = format_output_for_docx(output_text)
                doc.add_paragraph(formatted_output)
                doc.save(doc_filename)

                with open(doc_filename, "rb") as file:
                    st.download_button(
                        label="📄 Download DOCX",
                        data=file,
                        file_name=doc_filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

            except Exception as e:
                st.error(f"⚠️ Error generating runbook: {str(e)}")
        else:
            st.warning("⚠️ Please confirm the AI prompt before generating the runbook.")

def format_output_for_docx(output: str) -> str:
    """Formats markdown-like output to docx-friendly HTML-style tags."""
    if not output:
        return ""
    
    formatted_text = output
    formatted_text = re.sub(r"^## (.*)", r"\n\n\1\n", formatted_text, flags=re.MULTILINE)
    formatted_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", formatted_text)
    formatted_text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", formatted_text)

    return formatted_text

#### Prompts Here #####

def query_utility_providers():
    """
    Queries Mistral AI for public utility providers based on city and ZIP code 
    stored in st.session_state. Stores and returns results in session state.
    """
    city = st.session_state.get("city", "").strip()
    zip_code = st.session_state.get("zip_code", "").strip()

    if not city or not zip_code:
        st.warning("City and ZIP code must be provided in session state.")
        return {
            "electricity": "Missing input",
            "natural_gas": "Missing input",
            "water": "Missing input"
        }

    prompt = f"""
You are a reliable assistant helping users prepare emergency documentation. 
Given the city: {city} and ZIP code: {zip_code}, list the **primary public utility provider companies** for the following:

1. Electricity
2. Natural Gas
3. Water

For each, provide only the company name. Format your response like this:

Electricity Provider: <company name>
Natural Gas Provider: <company name>
Water Provider: <company name>
"""

    try:
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[UserMessage(content=prompt)],
            max_tokens=1500,
            temperature=0.5,
        )
        content = response.choices[0].message.content
    except Exception as e:
        st.error(f"Error querying Mistral API: {str(e)}")
        content = ""

    def extract(label):
        match = re.search(rf"{label} Provider:\s*(.+)", content)
        return match.group(1).strip() if match else "Not found"

    electricity = extract("Electricity")
    natural_gas = extract("Natural Gas")
    water = extract("Water")

    st.session_state["electricity_provider"] = electricity
    st.session_state["natural_gas_provider"] = natural_gas
    st.session_state["water_provider"] = water

    return {
        "electricity": electricity,
        "natural_gas": natural_gas,
        "water": water
    }

def utilities_emergency_runbook_prompt(
            city=st.session_state.get("city", ""),
            zip_code=st.session_state.get("zip_code", ""),
            internet_provider_name=st.session_state.get("internet_provider",""),
            electricity_provider_name=st.session_state.get("electricity_provider",""),
            natural_gas_provider_name=st.session_state.get("natural_gas_provider",""),
            water_provider_name=st.session_state.get("water_provider","")
        ):

    return f"""
You are an expert assistant generating a city-specific Emergency Preparedness Run Book. First, search the internet for up-to-date local utility providers and their emergency contact information. Then, compose a comprehensive, easy-to-follow guide customized for residents of City: {city}, Zip Code: {zip_code}.

Start by identifying the following utility/service providers for the specified location:
- Internet Provider Name
- Electricity Provider Name
- Natural Gas Provider Name
- Water Provider Name

For each provider, retrieve:
- Company Description
- Customer Service Phone Number
- Customer Service Address (if available)
- Official Website
- Emergency Contact Numbers (specific to outages, leaks, service disruptions)
- Steps to report issues

---


### 📕 Emergency Run Book

#### ⚡ 1. Electricity – {electricity_provider_name}
- Provider Description
- Customer Service
- Website
- Emergency Contact

**Power Outage Response Guide:**
- Steps to follow
- How to report
- Safety precautions

---
#### 🔥 2. Natural Gas – {natural_gas_provider_name}
- Provider Description
- Customer Service
- Website
- Emergency Contact

**Gas Leak Response Guide:**
- Signs and precautions
- How to evacuate
- How to report

---
#### 💧 3. Water – {water_provider_name}
- Provider Description
- Customer Service
- Website
- Emergency Contact

**Water Outage or Leak Guide:**
- Detection steps
- Shutoff procedure

---
#### 🌐 4. Internet – {internet_provider_name}
- Provider Description
- Customer Service
- Website
- Emergency Contact

**Internet Outage Response Guide:**
- Troubleshooting
- Reporting
- Staying informed
---

Ensure the run book is clearly formatted using Markdown, with bold headers and bullet points. Use ⚠️ to highlight missing kit items.
""".strip()

def format_output_for_docx(output: str) -> str:
    """Formats markdown-like output to docx-friendly HTML-style tags."""
    if not output:
        return ""
    
    formatted_text = output
    formatted_text = re.sub(r"^## (.*)", r"\n\n\1\n", formatted_text, flags=re.MULTILINE)
    formatted_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", formatted_text)
    formatted_text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", formatted_text)

    return formatted_text

###### Main Functions that comprise of the Levels

### Leve 1 - Home

def home():
    st.write("Let's gather some information. Please enter your details:")

    # Input fields
    st.session_state.city = st.text_input("City", value=st.session_state.get("city", ""))
    st.session_state.zip_code = st.text_input("ZIP Code", value=st.session_state.get("zip_code", ""))
    st.session_state.internet_provider = st.text_input("Internet Provider", value=st.session_state.get("internet_provider", ""))

    # Step 1: Fetch utility providers
    if st.button("Find My Utility Providers"):
        with st.spinner("Fetching providers from Mistral..."):
            results = query_utility_providers()
            st.success("Providers stored in session state!")

    # Step 2: Allow corrections
    st.write("Correct Utility Providers:")

    correct_electricity = st.checkbox("Correct Electricity Provider", value=False)
    corrected_electricity = st.text_input("Electricity Provider", value=st.session_state.get("electricity_provider", ""), disabled=not correct_electricity)

    correct_natural_gas = st.checkbox("Correct Natural Gas Provider", value=False)
    corrected_natural_gas = st.text_input("Natural Gas Provider", value=st.session_state.get("natural_gas_provider", ""), disabled=not correct_natural_gas)

    correct_water = st.checkbox("Correct Water Provider", value=False)
    corrected_water = st.text_input("Water Provider", value=st.session_state.get("water_provider", ""), disabled=not correct_water)

    if st.button("Save Utility Providers"):
        if correct_electricity:
            st.session_state["electricity_provider"] = corrected_electricity
        if correct_natural_gas:
            st.session_state["natural_gas_provider"] = corrected_natural_gas
        if correct_water:
            st.session_state["water_provider"] = corrected_water
        st.success("Utility providers updated!")

    # Step 3: Preview prompt
    with st.expander("Confirm AI Prompt Preview by Selecting the button inside"):
        user_confirmation = st.checkbox("Show AI Prompt")
        st.session_state["user_confirmation"] = user_confirmation  # store confirmation in session

        if user_confirmation:
            prompt = utilities_emergency_runbook_prompt(
                city=st.session_state.get("city", ""),
                zip_code=st.session_state.get("zip_code", ""),
                internet_provider_name=st.session_state.get("internet_provider", ""),
                electricity_provider_name=st.session_state.get("electricity_provider", ""),
                natural_gas_provider_name=st.session_state.get("natural_gas_provider", ""),
                water_provider_name=st.session_state.get("water_provider", "")
            )
            st.code(prompt, language="markdown")
            st.session_state["generated_prompt"] = prompt  # Save for use below

    # Step 4: Generate runbook using reusable function
    st.write("Next, click the button to generate your personalized utilities emergency runbook document:")

    generate_runbook_from_prompt(
        prompt=st.session_state.get("generated_prompt", ""),
        api_key=os.getenv("MISTRAL_TOKEN"),
        button_text="Complete Level 1 Mission",
        doc_heading="Home Utilities Emergency Runbook",
        doc_filename="home_utilities_emergency.docx"
    )

### Level 2 - Home

### Call App Functions
if __name__ == "__main__":
    main()