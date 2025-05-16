import streamlit as st
import re
from mistralai import Mistral, UserMessage
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime, timedelta
from docx import Document
from docx.text.run import Run
import re
import time
from PIL import Image
import io
import uuid
import json
from docx.oxml.ns import nsdecls
from docx.oxml import OxmlElement

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to Home Hero Academy! 👋")

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
import streamlit as st
import json
import os

PROGRESS_FILE = "user_progress.json"

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)

def main():
    levels = ("Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Bonus Level")

    # Initialize session state
    if "section" not in st.session_state:
        st.session_state.section = levels[0]

    if "progress" not in st.session_state:
        st.session_state.progress = load_progress()

    # Sidebar navigation
    selected = st.sidebar.radio(
        "Choose a Level:",
        levels,
        index=levels.index(st.session_state.section)
    )

    # Progress bar in sidebar
    st.sidebar.markdown("## 🧭 Progress")
    for i in range(1, 6):
        key = f"level_{i}_completed"
        label = f"Level {i}"
        if st.session_state.progress.get(key):
            st.sidebar.success(f"✅ {label}")
        else:
            st.sidebar.info(f"🔒 {label}")

    bonus = st.session_state.progress.get("bonus_completed", False)
    st.sidebar.markdown("✅ Bonus Level" if bonus else "🔒 Bonus Level")

    # Enforce Level 1 lock
    if selected != "Level 1" and not st.session_state.progress.get("level_1_completed", False):
        st.warning("🚧 Please complete Level 1 before accessing other levels.")
        st.session_state.section = "Level 1"
    else:
        st.session_state.section = selected

    # Render level
    section = st.session_state.section

    if section == "Level 1":
        st.subheader("🏁 Welcome to Level 1")
        home()  # ← call logic here that sets progress and saves

    elif section == "Level 2":
        st.subheader("🔧 Level 2 Tools")
        emergency_kit_utilities()

    elif section == "Level 3":
        st.subheader("📊 Level 3 Data")
        mail_trash_handling()

    elif section == "Level 4":
        st.subheader("🧠 Level 4 Analysis")
        security_convenience_ownership()

    elif section == "Level 5":
        st.subheader("🚀 Level 5 Launch")
        emergency_kit_critical_documents()

    elif section == "Bonus Level":
        st.subheader("🎁 Bonus Level Content")

    # Optional: Reset button
    if st.sidebar.button("🔄 Reset Progress"):
        st.session_state.progress = {}
        save_progress({})
        st.experimental_rerun()

#### Reusable Functions to Generate and Format Runbooks #####
def format_output_for_docx(output: str) -> str:
    """Formats markdown-like output to docx-friendly text with HTML-like formatting."""
    if not output:
        return ""

    # Convert markdown-like headings to <h2>, <h3>, <h4>
    formatted_text = re.sub(r"^## (.*)", r"<h2>\1</h2>", output, flags=re.MULTILINE)  # Convert ## to <h2>
    formatted_text = re.sub(r"^### (.*)", r"<h3>\1</h3>", formatted_text, flags=re.MULTILINE)  # Convert ### to <h3>
    formatted_text = re.sub(r"^#### (.*)", r"<h4>\1</h4>", formatted_text, flags=re.MULTILINE)  # Convert #### to <h4>

    # Convert markdown-style bold and italic to HTML-like <b> and <i>
    formatted_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", formatted_text)  # Convert **bold** to <b>
    formatted_text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", formatted_text)  # Convert *italic* to <i>

    # Convert markdown-style links [text](url) to <a> tags
    formatted_text = re.sub(r"\[([^\]]+)\]\((http[^\)]+)\)", r"<a href='\2'>\1</a>", formatted_text)

    # Convert markdown dashes to unordered list <ul><li> items
    formatted_text = re.sub(r"^-\s(.*)", r"<ul><li>\1</li></ul>", formatted_text, flags=re.MULTILINE)

    return formatted_text

def save_docx_from_formatted_text(formatted_text: str, doc_filename: str, doc_heading: str):
    """Saves the formatted text into a DOCX file with proper formatting, including links and bullet points."""
    doc = Document()
    doc.add_heading(doc_heading, 0)

    # Split the formatted text by paragraphs and process each paragraph
    paragraphs = formatted_text.split('\n\n')

    for para in paragraphs:
        # Create a paragraph in the DOCX file
        doc_paragraph = doc.add_paragraph()

        # Handle bold, italic, hyperlinks, and bullet points
        runs = re.split(r'(<b>.*?</b>|<i>.*?</i>|<a href=.*?>.*?</a>|<ul><li>.*?</li></ul>|<h2>.*?</h2>|<h3>.*?</h3>|<h4>.*?</h4>)', para)  # Split by bold, italic, link, or bullet tags

        # First, process headings (<h2>, <h3>, <h4>) before italic
        for run in runs:
            if run.startswith('<h2>'):
                run_text = run[4:-5]  # Remove <h2> and </h2>
                doc.add_heading(run_text, level=2)
            elif run.startswith('<h3>'):
                run_text = run[4:-5]  # Remove <h3> and </h3>
                doc.add_heading(run_text, level=3)
            elif run.startswith('<h4>'):
                run_text = run[4:-5]  # Remove <h4> and </h4>
                doc.add_heading(run_text, level=4)

        # Next, process bold text (<b>...</b>)
        for run in runs:
            if run.startswith('<b>'):
                run_text = run[3:-4]  # Remove <b> and </b>
                doc_paragraph.add_run(run_text).bold = True

        # Then process hyperlinks (<a href=...>)
        for run in runs:
            if run.startswith('<a href='):
                # Extract the link and text from <a href="url">text</a>
                match = re.match(r'<a href="(.*?)">(.*?)</a>', run)
                if match:
                    url = match.group(1)
                    text = match.group(2)
                    # Add the hyperlink to the document
                    run_obj = doc_paragraph.add_run(text)
                    # Creating the hyperlink element (using lxml)
                    hyperlink = OxmlElement('w:hyperlink')
                    hyperlink.set(nsdecls('w'), 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')
                    r = OxmlElement('w:r')
                    rPr = OxmlElement('w:rPr')
                    rPr.append(OxmlElement('w:rStyle'))
                    r.append(rPr)
                    r.text = text
                    hyperlink.append(r)
                    doc_paragraph._element.append(hyperlink)

        # After bold and hyperlinks, process italic (<i>...</i>) formatting
        for run in runs:
            if run.startswith('<i>'):
                run_text = run[3:-4]  # Remove <i> and </i>
                doc_paragraph.add_run(run_text).italic = True

        # Process bullet points (<ul><li>...</li></ul>)
        for run in runs:
            if run.startswith('<ul>'):
                # Process bullet points (unordered list)
                items = re.findall(r'<li>(.*?)</li>', run)
                for item in items:
                    doc_paragraph = doc.add_paragraph(item, style='ListBullet')
            else:
                doc_paragraph.add_run(run)

    doc.save(doc_filename)

def generate_runbook_from_prompt(
    prompt: str,
    api_key: str,
    button_text: str,
    doc_heading: str,
    doc_filename: str
):
    """
    Reusable Streamlit function to handle LLM completion and export a DOCX or HTML file.
    """
    unique_key = f"{button_text.lower().replace(' ', '_')}_button"
    clicked = st.button(button_text, key=unique_key)

    if clicked:
        st.write("✅ Button was clicked")

        if st.session_state.get("user_confirmation") and prompt:
            try:
                st.write("⏳ Sending to Mistral...")

                client = Mistral(api_key=api_key)
                completion = client.chat.complete(
                    model="mistral-small-latest",
                    messages=[UserMessage(content=prompt)],
                    max_tokens=1500,
                    temperature=0.5,
                )

                output = completion.choices[0].message.content
                st.success(f"{doc_heading} generated successfully!")
                st.write(output)

                # Format the output into HTML-like format
                formatted_output = format_output_for_docx(output)

                # Saving to DOCX
                if doc_filename.endswith(".docx"):
                    save_docx_from_formatted_text(formatted_output, doc_filename, doc_heading)

                    with open(doc_filename, "rb") as f:
                        st.download_button(
                            label="📄 Download DOCX",
                            data=f,
                            file_name=doc_filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                # Saving to HTML (Optional for HTML output)
                elif doc_filename.endswith(".html"):
                    html_content = f"<html><head><title>{doc_heading}</title></head><body>{formatted_output}</body></html>"

                    with open(doc_filename, "w") as f:
                        f.write(html_content)

                    with open(doc_filename, "rb") as f:
                        st.download_button(
                            label="📄 Download HTML",
                            data=f,
                            file_name=doc_filename,
                            mime="text/html"
                        )

            except Exception as e:
                st.error(f"❌ Failed to generate runbook: {str(e)}")

        else:
            st.warning("⚠️ Prompt not confirmed or missing.")

def generate_runbook_from_prompt_split(
    prompt_emergency: str,
    prompt_mail_trash: str,
    api_key: str,
    button_text: str,
    doc_heading: str,
    doc_filename: str
):
    """
    Calls Mistral API with two prompts: emergency/utilities and mail/trash.
    Concatenates results and creates a formatted DOCX file.
    """
    unique_key = f"{button_text.lower().replace(' ', '_')}_button"
    clicked = st.button(button_text, key=unique_key)

    # 🔍 Debug Info
    with st.expander("🧪 Debug Info (Prompt + State)"):
        st.write("🔘 **Button Clicked:**", "✅ Yes" if clicked else "❌ No")
        st.write("🙋 **User Confirmed Prompt:**", st.session_state.get("user_confirmation", False))
        st.write("🔑 **API Key Loaded:**", "✅ Yes" if api_key else "❌ No")

    # Check each prompt presence
        st.write("📄 **Emergency Prompt Exists:**", "✅ Yes" if prompt_emergency else "❌ No")
        if prompt_emergency:
            st.code(prompt_emergency[:500] + "..." if len(prompt_emergency) > 500 else prompt_emergency, language="markdown")

        st.write("📬 **Mail & Trash Prompt Exists:**", "✅ Yes" if prompt_mail_trash else "❌ No")
        if prompt_mail_trash:
            st.code(prompt_mail_trash[:500] + "..." if len(prompt_mail_trash) > 500 else prompt_mail_trash, language="markdown")

    # Optionally display selected session state keys
        st.write("📋 **Selected Session State Keys:**")
        st.json({key: st.session_state.get(key) for key in [
            "user_confirmation",
            "electricity_provider",
            "natural_gas_provider",
            "water_provider",
            "internet_provider",
            "emergency_kit_status",
            "emergency_kit_location"
        ]})

    if clicked:
        st.write("✅ Button was clicked")

        if not st.session_state.get("user_confirmation", False):
            st.warning("⚠️ Please confirm the AI prompt before generating the runbook.")
            return

        try:
            client = Mistral(api_key=api_key)

            st.info("📡 Querying Mistral for Emergency & Utilities Section...")
            emergency_response = client.chat.complete(
                model="mistral-small-latest",
                messages=[UserMessage(content=prompt_emergency)],
                max_tokens=1500,
                temperature=0.5,
            ).choices[0].message.content

            st.info("📬 Querying Mistral for Mail & Trash Section...")
            mail_trash_response = client.chat.complete(
                model="mistral-small-latest",
                messages=[UserMessage(content=prompt_mail_trash)],
                max_tokens=1000,
                temperature=0.5,
            ).choices[0].message.content

            # Combine sections and format for DOCX
            full_output = f"{emergency_response}\n\n{mail_trash_response}"
            formatted_output = format_output_for_docx(full_output)

            st.success(f"{doc_heading} generated successfully!")
            st.write(full_output)

            # Write to DOCX
            doc = Document()
            doc.add_heading(doc_heading, 0)
            doc.add_paragraph(formatted_output)
            doc.save(doc_filename)

            # Download button
            with open(doc_filename, "rb") as f:
                st.download_button(
                    label="📄 Download DOCX",
                    data=f,
                    file_name=doc_filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

        except Exception as e:
            st.error(f"❌ Error generating runbook: {str(e)}")

def generate_runbook_from_multiple_prompts(
    prompts: list,
    api_key: str,
    button_text: str,
    doc_heading: str,
    doc_filename: str
):
    """
    Calls Mistral API with a list of prompts, concatenates results,
    formats the content, and generates a downloadable DOCX.
    """
    unique_key = f"{button_text.lower().replace(' ', '_')}_button"
    clicked = st.button(button_text, key=unique_key)

    # 🔍 Debug Info
    with st.expander("🧪 Debug Info (Prompt + State)"):
        st.write("🔘 **Button Clicked:**", "✅ Yes" if clicked else "❌ No")
        st.write("🙋 **User Confirmed Prompt:**", st.session_state.get("user_confirmation", False))
        st.write("🔑 **API Key Loaded:**", "✅ Yes" if api_key else "❌ No")

        for idx, prompt in enumerate(prompts):
            label = f"Prompt #{idx + 1}"
            st.write(f"📄 **{label} Exists:**", "✅ Yes" if prompt else "❌ No")
            if prompt:
                st.code(prompt[:500] + "..." if len(prompt) > 500 else prompt, language="markdown")

    if clicked:
        if not st.session_state.get("user_confirmation", False):
            st.warning("⚠️ Please confirm the AI prompt before generating the runbook.")
            return

        try:
            client = Mistral(api_key=api_key)
            combined_output = ""

            for idx, prompt in enumerate(prompts):
                st.info(f"📡 Querying Mistral for Section {idx + 1}...")
                response = client.chat.complete(
                    model="mistral-small-latest",
                    messages=[UserMessage(content=prompt)],
                    max_tokens=1500,
                    temperature=0.5,
                )
                combined_output += response.choices[0].message.content + "\n\n"

            formatted_output = format_output_for_docx(combined_output)

            st.success(f"{doc_heading} generated successfully!")
            st.write(combined_output)

            # Write to DOCX
            doc = Document()
            doc.add_heading(doc_heading, 0)
            doc.add_paragraph(formatted_output)
            doc.save(doc_filename)

            with open(doc_filename, "rb") as f:
                st.download_button(
                    label="📄 Download DOCX",
                    data=f,
                    file_name=doc_filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

        except Exception as e:
            st.error(f"❌ Error generating runbook: {str(e)}")


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

#### Emergency Kit + Utilities Prompt ####

def emergency_kit_utilities_runbook_prompt(
            city=st.session_state.get("city", ""),
            zip_code=st.session_state.get("zip_code", ""),
            internet_provider_name=st.session_state.get("internet_provider",""),
            electricity_provider_name=st.session_state.get("electricity_provider",""),
            natural_gas_provider_name=st.session_state.get("natural_gas_provider",""),
            water_provider_name=st.session_state.get("water_provider",""),
            emergency_kit_status=st.session_state.get("emergency_kit_status", "No"),
            emergency_kit_location=st.session_state.get("emergency_kit_location", ""),
            selected_items=st.session_state.get("homeowner_kit_stock", []),
            not_selected_items=st.session_state.get("homeowner_kit_stock", []),
            flashlights_info=st.session_state.get("flashlights_info", ""),
            radio_info=st.session_state.get("radio_info", ""),
            food_water_info=st.session_state.get("food_water_info", ""),
            important_docs_info=st.session_state.get("important_docs_info", ""),
            whistle_info=st.session_state.get("whistle_info", ""),
            medications_info=st.session_state.get("medications_info", ""),
            mask_info=st.session_state.get("mask_info", ""),
            maps_contacts_info=st.session_state.get("maps_contacts_info", "")
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

For Emergency Kit Summary, if {emergency_kit_status} is Yes, then write that the emergency kit is available and where it's located using {emergency_kit_location}, if {emergency_kit_status} is No then write the Emergency kit is a work in progress and will be located using {emergency_kit_location}.

Retrieve Emergency contact informtion for local:
- Police
- Fire Department
- Hospital
- Posion Control

---

### 🧰 Emergency Kit Summary

**Kit Inventory:**
{selected_items}

**"⚠️ Consider adding the following items to your emergency kit:"
{not_selected_items}

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
- **Recommended Kit Items**:
  - {flashlights_info}
  - {radio_info}
  - {food_water_info}
  - {important_docs_info}

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
- **Recommended Kit Items**:
  - {whistle_info}
  - {important_docs_info}
  - {flashlights_info}

---

#### 💧 3. Water – {water_provider_name}
- Provider Description
- Customer Service
- Website
- Emergency Contact

**Water Outage or Leak Guide:**
- Detection steps
- Shutoff procedure
- **Recommended Kit Items**:
  - {food_water_info}
  - {medications_info}
  - {mask_info}
  - {important_docs_info}

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
- **Recommended Kit Items**:
  - {radio_info}
  - {maps_contacts_info}
  - {important_docs_info}

---

Ensure the run book is clearly formatted using Markdown, with bold headers and bullet points. Use ⚠️ to highlight missing kit items.
""".strip()

#### Mail + Trash Prompt ####
def mail_trash_runbook_prompt():
    mail_info = st.session_state.get("mail_info", {})
    mailbox_location = mail_info.get("Mailbox Location", "Not provided")
    mailbox_key = mail_info.get("Mailbox Key", "Not provided")
    pick_up_schedule = mail_info.get("Pick-Up Schedule", "Not provided")
    what_to_do_with_mail = mail_info.get("What to Do with the Mail", "Not provided")
    what_to_do_with_packages = mail_info.get("Packages", "Not provided")
    trash_info = st.session_state.get("trash_info", {})
    indoor = trash_info.get("indoor", {})
    outdoor = trash_info.get("outdoor", {})
    schedule = trash_info.get("schedule", {})
    composting = trash_info.get("composting", {})
    common_disposal = trash_info.get("common_disposal", {})
    wm = trash_info.get("waste_management", {})

    return f"""
You are an expert assistant generating Mail and Waste Management Run Book. Compose a comprehensive, easy-to-follow guide for house stitters and people watching the house when occupants are out of town. For any values set to No please omit thoses lines.

### 📕 Mail Handling and Waste Management Instructions 

#### 📬 Mail Handling Instructions

- **Mailbox Location**: {mailbox_location}
- **Mailbox Key Info**: {mailbox_key}
- **Pick-Up Schedule**: {pick_up_schedule}
- **Mail Sorting Instructions**: {what_to_do_with_mail}
- **Delivery Packages**: {what_to_do_with_packages}

---

#### 🗑️ Trash & Recycling Instructions

**Indoor Trash**
- Kitchen Trash: {indoor.get("kitchen_bin", "Not provided")}
- Bathroom Trash: {indoor.get("bathroom_bin", "Not provided")}
- Other Rooms Trash: {indoor.get("other_room_bin", "Not provided")}

**Outdoor Bins**
- Please take the bins: {outdoor.get("bin_destination", "Not provided")}
- Bins Description: {outdoor.get("bin_description", "Not provided")}
- Location: {outdoor.get("bin_location_specifics", "Not provided")}
- Instructions: {outdoor.get("bin_handling_instructions", "Not provided")}

**Collection Schedule**
- Garbage Pickup: {schedule.get("trash_day", "Not provided")}, {schedule.get("trash_time", "Not provided")}
- Recycling Pickup: {schedule.get("recycling_day", "Not provided")}, {schedule.get("recycling_time", "Not provided")}

**Composting**
- Composting Used: {"Yes" if composting.get("compost_used", False) else "No"}
- Compost Instructions: {composting.get("compost_instructions", "N/A")}

**Common Disposal Area**
- Used: {"Yes" if common_disposal.get("uses_common_disposal", False) else "No"}
- Instructions: {common_disposal.get("common_area_instructions", "N/A")}

**Waste Management Contact**
- Company Name: {wm.get("company_name", "Not provided")}
- Phone: {wm.get("phone", "Not provided")}
- Contact: {wm.get("description", "Not provided")}

---

Ensure the run book is clearly formatted using Markdown, with bold headers and bullet points. Use ⚠️ to highlight missing kit items.
""".strip()

#### Security and Services Prompt ####

def home_caretaker_runbook_prompt():
    csi = st.session_state.get("convenience_seeker_info", {})
    roi = st.session_state.get("rent_own_info", {})
    hsi = st.session_state.get("home_security_info", {})

    return f"""
You are a helpful assistant tasked with generating a professional, detailed, and easy-to-follow Home Caretaker & Guest Runbook. The goal is to ensure a smooth experience for caretakers or guests while the home occupants are away. 

Please use the following information provided by the homeowner to write a clear and structured guide:
Please omit any headings that return "Not provided" for all the values below it.
Please omit any sub-headings that return "Not provided" for all the values below it.
Please omit any lines that return "Not provided" or "N/A".
Please omit any sub-headings that return "Not provided" or "N/A" for all the values below it.
Please don't add a title to the runbook.

### 📕 Security and Services Guide

#### 🔐 Home Security & Technology
- Security Company Name: {hsi.get("home_security_comp_name", "Not provided")}
- Security Company Number: {hsi.get("home_security_comp_num", "Not provided")}
- Arming/Disarming Instructions: {hsi.get("arm_disarm_instructions", "Not provided")}
- If Alert is Triggered: {hsi.get("security_alert_steps", "Not provided")}
- Indoor Camera Notes: {hsi.get("indoor_cameras", "Not provided")}
- Emergency Access Instructions: {hsi.get("access_emergency", "Not provided")}
- Wi-Fi Info Location: {hsi.get("wifi_network_name", "Not provided")}
- Guest Wi-Fi Access: {hsi.get("wifi_guests", "Not provided")}
- Landline/VOIP Notes: {hsi.get("landline_voip", "Not provided")}

---

#### 🧹 Cleaning Service Instructions
- Company Name: {csi.get("cleaning_name", "Not provided")}
- Phone Number: {csi.get("cleaning_number", "Not provided")}
- Schedule: {csi.get("cleaning_schedule", "Not provided")}
- Access Method: {csi.get("cleaning_access", "Not provided")}
- Post-Cleaning Procedures: {csi.get("cleaning_finish_steps", "Not provided")}
- Crew Identity Verification: {csi.get("cleaning_identity_confirmation", "Not provided")}

---

#### 🌿 Gardening & Landscape Service Instructions
- Company Name: {csi.get("gardening_name", "Not provided")}
- Phone Number: {csi.get("gardening_number", "Not provided")}
- Schedule: {csi.get("gardening_schedule", "Not provided")}
- Access Method: {csi.get("gardening_access", "Not provided")}
- Post-Service Procedures: {csi.get("gardening_finish_steps", "Not provided")}
- Crew Identity Verification: {csi.get("gardening_identity_confirmation", "Not provided")}

---

#### 🏊 Pool Maintenance Instructions
- Company Name: {csi.get("pool_name", "Not provided")}
- Phone Number: {csi.get("pool_number", "Not provided")}
- Schedule: {csi.get("pool_schedule", "Not provided")}
- Access Method: {csi.get("pool_access", "Not provided")}
- Post-Service Procedures: {csi.get("pool_finish_steps", "Not provided")}
- Crew Identity Verification: {csi.get("pool_identity_confirmation", "Not provided")}

---

#### 🏢 Property Management (Renters or HOA)
- Company Name: {roi.get("property_management_name", "Not provided")}
- Phone Number: {roi.get("property_management_number", "Not provided")}
- Email: {roi.get("property_management_email", "Not provided")}
- When to Contact: {roi.get("property_management_description", "Not provided")}

---

#### 🛠️ Service Contacts (For Homeowners)
**Handyman**
- Name: {roi.get("handyman_name", "N/A")}
- Phone: {roi.get("handyman_number", "N/A")}
- When to Contact: {roi.get("handyman_description", "N/A")}

**Electrician**
- Name: {roi.get("electrician_name", "N/A")}
- Phone: {roi.get("electrician_number", "N/A")}
- When to Contact: {roi.get("electrician_description", "N/A")}

**Exterminator**
- Name: {roi.get("exterminator_name", "N/A")}
- Phone: {roi.get("exterminator_number", "N/A")}
- When to Contact: {roi.get("exterminator_description", "N/A")}

**Plumber**
- Name: {roi.get("plumber_name", "N/A")}
- Phone: {roi.get("plumber_number", "N/A")}
- When to Contact: {roi.get("plumber_description", "N/A")}

---

Please format the runbook clearly with headers and bullet points. Use “⚠️ Not provided” as a flag for incomplete or missing info that should be reviewed.
""".strip()


###### Main Functions that comprise of the Levels

### Leve 1 - Home

def home_debug():

    st.write("🟡 About to render runbook button")

    generate_runbook_from_prompt(
        prompt=st.session_state.get("generated_prompt", ""),
        api_key=os.getenv("MISTRAL_TOKEN"),
        button_text="Complete Level 1 Mission",
        doc_heading="Home Utilities Emergency Runbook",
        doc_filename="home_utilities_emergency.html"
    )
    st.write("🟢 After button render")

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
    # Move this outside the expander
    user_confirmation = st.checkbox("✅ Confirm AI Prompt")
    st.session_state["user_confirmation"] = user_confirmation # store confirmation in session

    if user_confirmation:
        prompt = utilities_emergency_runbook_prompt()
        st.session_state["generated_prompt"] = prompt
    else:
        st.session_state["generated_prompt"] = None

    st.session_state.progress["level_1_completed"] = True
    save_progress(st.session_state.progress)


# Show prompt in expander
    with st.expander("AI Prompt Preview (Optional)"):
        if st.session_state.get("generated_prompt"):
            st.code(st.session_state["generated_prompt"], language="markdown")

    # Step 4: Generate runbook using reusable function
    st.write("Next, click the button to generate your personalized utilities emergency runbook document:")
    
    if not st.session_state.get("generated_prompt"):
        st.warning("⚠️ Prompt not ready. Please confirm the prompt first.")
        return
    
    #st.write("Prompt preview (sanity check):", st.session_state.get("generated_prompt", "[Empty]"))

    generate_runbook_from_prompt(
        prompt=st.session_state.get("generated_prompt", ""),
        api_key=os.getenv("MISTRAL_TOKEN"),
        button_text="Complete Level 1 Mission",
        doc_heading="Home Utilities Emergency Runbook",
        doc_filename="home_utilities_emergency.docx"
    )
    #st.write("🧪 Debug Info:")
    #st.write("Prompt exists:", "Yes" if st.session_state.get("generated_prompt") else "No")
    #st.write("User confirmed:", st.session_state.get("user_confirmation"))
    #st.write("Prompt:", st.session_state.get("generated_prompt"))
    #st.write("API key loaded:", "Yes" if os.getenv("MISTRAL_TOKEN") else "No")


### Level 2 - Emergency Kit Details

# Define the homeowner_kit_stock function
def homeowner_kit_stock():
    kit_items = [
        "Flashlights and extra batteries",
        "First aid kit",
        "Non-perishable food and bottled water",
        "Medications and personal hygiene items",
        "Important documents (insurance, identification)",
        "Battery-powered or hand-crank radio",
        "Whistle (for signaling)",
        "Dust masks (for air filtration)",
        "Local maps and contact lists"
    ]

    # Initialize all session state variables to None
    for item in kit_items:
        key = item.lower().replace(" ", "_").replace("(", "").replace(")", "") + "_storage"
        if key not in st.session_state:
            st.session_state[key] = None

    with st.form(key='emergency_kit_form'):
        selected_items = st.multiselect(
            "Select all you have:",
            kit_items
        )
        submit_button = st.form_submit_button(label='Submit')

    if submit_button:
        not_selected_items = [item for item in kit_items if item not in selected_items]

        if not_selected_items:
            st.warning("⚠️ Consider adding the following items to your emergency kit:")
            for item in not_selected_items:
                st.write(f"- {item}")

        # Update session state
        for item in kit_items:
            key = item.lower().replace(" ", "_").replace("(", "").replace(")", "") + "_storage"
            if item in selected_items:
                st.session_state[key] = item
            else:
                st.session_state[key] = None

    return selected_items

def emergency_kit():
    st.write("Emergency Kit Status")

    # Use st.radio to create a dropdown menu for selecting between renting or owning
    emergency_kit_status = st.radio(
        'Do you have an Emergency Kit?',  # Label for the widget
        ('Yes', 'No')  # Options to display in the dropdown menu
    )

    kit_items = [
        "Flashlights and extra batteries",
        "First aid kit",
        "Non-perishable food and bottled water",
        "Medications and personal hygiene items",
        "Important documents (insurance, identification)",
        "Battery-powered or hand-crank radio",
        "Whistle (for signaling)",
        "Dust masks (for air filtration)",
        "Local maps and contact lists"
    ]

    if emergency_kit_status == 'Yes':
        st.write("Emergency Kit Info")
        st.success('This is a success message!', icon=":material/medical_services:")
        st.session_state['emergency_kit_status'] = emergency_kit_status

        emergency_kit_location = st.text_area("Where is the Emergency Kit located?")
        if emergency_kit_location:
            st.session_state['emergency_kit_location'] = emergency_kit_location

        # Call the homeowner_kit_stock function and get the selected items
        selected_items = homeowner_kit_stock()
        if selected_items:
            st.session_state['homeowner_kit_stock'] = selected_items

        # Determine not selected items
        not_selected_items = [item for item in kit_items if item not in selected_items]
        st.session_state['not_selected_items'] = not_selected_items

    else:
        st.write("Emergency Kit Info")
        st.warning("⚠️ Let's build your emergency kit with what you have.")

        emergency_kit_location = st.text_area("Where do you want to put your emergency kit items?")
        if emergency_kit_location:
            st.session_state['emergency_kit_location'] = emergency_kit_location

        # Call the homeowner_kit_stock function and get the selected items
        selected_items = homeowner_kit_stock()
        if selected_items:
            st.session_state['homeowner_kit_stock'] = selected_items

        # Determine not selected items
        not_selected_items = [item for item in kit_items if item not in selected_items]
        st.session_state['not_selected_items'] = not_selected_items

        st.success("📦 Emergency Kit Built!")

    return not_selected_items

def emergency_kit_utilities():

    # Step 1: Input fields
    emergency_kit()
    
    # Step 2: Preview prompt

    # Move this outside the expander
    user_confirmation = st.checkbox("✅ Confirm AI Prompt")
    st.session_state["user_confirmation"] = user_confirmation # store confirmation in session

    st.session_state.progress["level_2_completed"] = True
    save_progress(st.session_state.progress)

    if user_confirmation:
        prompt = emergency_kit_utilities_runbook_prompt()
        st.session_state["generated_prompt"] = prompt
    else:
        st.session_state["generated_prompt"] = None

# Show prompt in expander
    with st.expander("AI Prompt Preview (Optional)"):
        if st.session_state.get("generated_prompt"):
            st.code(st.session_state["generated_prompt"], language="markdown")

    # Step 3: Generate runbook using reusable function
    st.write("Next, click the button to generate your personalized utilities emergency runbook document:")

    generate_runbook_from_prompt(
        prompt=st.session_state.get("generated_prompt", ""),
        api_key=os.getenv("MISTRAL_TOKEN"),
        button_text="Complete Level 2 Mission",
        doc_heading="Home Emergency Runbook With Emergency Kit Summary",
        doc_filename="home_util_emergency_kit.docx"
    )
##### Level 3 - Mail Handling and Trash

def mail():
    st.subheader("📬 Mail Handling Instructions")

    if 'mail_info' not in st.session_state:
        st.session_state.mail_info = {}

    with st.expander("Mail Handling", expanded=True):
        # Input fields
        mailbox_location = st.text_area(
            "📍 Mailbox Location",
            placeholder="E.g., 'At the end of the driveway on the left side.'"
        )

        mailbox_key = st.text_area(
            "🔑 Mailbox Key (Optional)",
            placeholder="E.g., 'Hanging on the key hook next to the fridge.'"
        )

        pick_up_schedule = st.text_area(
            "📆 Mail Pick-Up Schedule",
            placeholder="E.g., 'Every other day' or 'Mondays and Thursdays'"
        )

        what_to_do_with_mail = st.text_area(
            "📥 What to Do with the Mail",
            placeholder="E.g., 'Place it in the tray on the kitchen counter.'"
        )

        What_to_do_with_packages = st.text_area(
            "📦 Packages",
            placeholder="E.g., 'Place it inside the entryway closet.'"
        )

        # Dynamic progress bar based on completion
        completed = sum([
            bool(mailbox_location),
            bool(mailbox_key),
            bool(pick_up_schedule),
            bool(what_to_do_with_mail),
            bool(What_to_do_with_packages)
        ])
        progress = int((completed / 5) * 100)
        st.progress(progress)

        # Save button
        if st.button("✅ Mail Handling 100% Complete. Click to Save"):
            st.session_state.mail_info = {
                "Mailbox Location": mailbox_location,
                "Mailbox Key": mailbox_key,
                "Pick-Up Schedule": pick_up_schedule,
                "What to Do with the Mail": what_to_do_with_mail,
                "Packages": What_to_do_with_packages
            }
            st.success("Mail handling instructions saved successfully!")

    # Display saved info
    st.subheader("📂 Saved Mail Handling Information")
    if st.session_state.mail_info:
        with st.expander("📋 Review Saved Info", expanded=True):
            for key, value in st.session_state.mail_info.items():
                st.markdown(f"**{key}:** {value}")
    else:
        st.info("No mail handling information saved yet.")

def trash_handling():
    st.markdown("## 🗑️ Trash Disposal Instructions")

    if 'trash_info' not in st.session_state:
        st.session_state.trash_info = {}
    if 'trash_images' not in st.session_state:
        st.session_state.trash_images = {}

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    times = ["Morning", "Afternoon", "Evening"]

    # --- Indoor Trash Info ---
    with st.expander("Kitchen and Bath Trash Details", expanded=True):
        st.markdown("##### Fill in the kitchen and bathroom trash info")

        kitchen_bin = st.text_area(
            "Kitchen Trash Bin Location, Emptying Schedule and Replacement Trash Bags", 
            placeholder="E.g. Bin is located under the kitchen sink. Empty when full.  Bags are next to the bin. They are labeled kitchen bags."
        )

        bathroom_bin = st.text_area(
            "Bathroom Trash Bin Emptying Schedule and Replacement Trash Bags ", 
            placeholder="E.g. Empty before Trash day.  Bags are under the sink."
        )

        other_room_bin = st.text_area(
            "Other Room Trash Bin Emptying Schedule and Replacement Trash Bags ", 
            placeholder="E.g. Empty before Trash day.  Bags are under the sinks of each bathroom."
        )

    # --- Outdoor Bin Info ---
    with st.expander("Outdoor Bin Details", expanded=True):
        st.markdown("##### Outdoor Bin Handling Details")

        bin_destination = st.text_area(
            "Where to Empty the Trash Bins", 
            placeholder="E.g. By the curb on pickup day"
        )

        bin_description = st.text_area(
            "What the Outdoor Trash Bins Look Like", 
            placeholder="E.g. Green with lid"
        )

        bin_location_specifics = st.text_area(
            "Specific Location or Instructions for Outdoor Bins", 
            placeholder="E.g. Next to side gate"
        )

        # Image upload helper
        def handle_image(label, display_name):
            image_key = f"{label} Image"
            if image_key not in st.session_state.trash_images:
                st.session_state.trash_images[image_key] = None

            if st.session_state.trash_images[image_key]:
                st.image(Image.open(io.BytesIO(st.session_state.trash_images[image_key])), caption=display_name)
                if st.button(f"Delete {display_name}", key=f"delete_{label}"):
                    st.session_state.trash_images[image_key] = None
                    st.experimental_rerun()
            else:
                uploaded = st.file_uploader(f"Upload a photo of the {display_name}", type=["jpg", "jpeg", "png"], key=f"{label}_upload")
                if uploaded:
                    st.session_state.trash_images[image_key] = uploaded.read()
                    st.success(f"{display_name} image uploaded.")
                    st.experimental_rerun()

        handle_image("Outdoor Bin", "Outdoor Trash Bin")
        handle_image("Recycling Bin", "Recycling Bin")

    # --- Collection Schedule ---
    with st.expander("Collection Schedule", expanded=True):
        st.markdown("##### Enter your trash and recycling schedule")
       
       #Collection Day + Time Pickers
        trash_day = st.selectbox("Garbage Pickup Day", days)
        trash_time = st.selectbox("Garbage Pickup Time", times)
        recycling_day = st.selectbox("Recycling Pickup Day", days)
        recycling_time = st.selectbox("Recycling Pickup Time", times)

        bin_handling_instructions = st.text_area("Instructions for Placing and Returning Outdoor Bins")

    # --- Common Disposal Area ---
    with st.expander("Common Disposal Area (if applicable)", expanded=True):
        st.markdown("##### Shared disposal area details")
        uses_common_disposal = st.checkbox("Is there a common disposal area?")

        if uses_common_disposal:
            common_area_instructions = st.text_area(
                "Instructions for Common Disposal Area", 
                placeholder="E.g. Dumpster in alley"
            )
            if common_area_instructions:
                handle_image("Common Area", "Common Disposal Area")

    # --- Composting ---
    with st.expander("Composting Instructions (if applicable)", expanded=True):
        st.markdown("##### Composting info")
        compost_applicable = st.checkbox("Is composting used?")

        if compost_applicable:
            compost_instructions = st.text_area(
                "Compost Instructions", 
                placeholder="E.g. Put organics in green bin"
            )

    # --- Waste Management Contact ---
    with st.expander("Waste Management Contact Info", expanded=True):
        st.markdown("##### Company contact details")

        wm_name = st.text_input(
            "Waste Management Company Name", 
            placeholder="E.g. WastePro"
        )
        wm_phone = st.text_input(
            "Contact Phone Number", 
            placeholder="E.g. (123) 456-7890"
            )
        wm_description = st.text_area(
            "When to Contact", 
            placeholder="E.g. Missed pickup or billing issues"
            )

# Dynamic progress bar based on completion
        total_sections = 6  # or 7 if compost is enabled
        filled_sections = sum([
            bool(kitchen_bin),
            bool(bathroom_bin),
            bool(other_room_bin),
            bool(bin_destination),
            bool(bin_description),
            bool(bin_location_specifics),
            bool(trash_day),
            bool(trash_time),
            bool(recycling_day),
            bool(recycling_time),
            bool(wm_name),
            bool(wm_phone),
            bool(wm_description),
            compost_applicable and bool(compost_instructions),
            uses_common_disposal and bool(common_area_instructions),
        ])

        total_progress = int((filled_sections / 16) * 100)
        st.progress(total_progress)

    # --- Save Button ---
    if st.button("✅ Trash Handling 100% Complete. Click to Save"):
        st.session_state.trash_info = {
            "indoor": {
                "kitchen_bin": kitchen_bin,
                "bathroom_bin": bathroom_bin,
                "other_room_bin": other_room_bin,
            },
            "outdoor": {
                "bin_destination": bin_destination,
                "bin_description": bin_description,
                "bin_location_specifics": bin_location_specifics,
                "bin_handling_instructions": bin_handling_instructions
            },
            "schedule": {
                "trash_day": trash_day,
                "trash_time": trash_time,
                "recycling_day": recycling_day,
                "recycling_time": recycling_time
            },
            "composting": {
                "compost_used": compost_applicable,
                "compost_instructions": compost_instructions if compost_applicable else "N/A"
            },
            "common_disposal": {
                "uses_common_disposal": uses_common_disposal,
                "common_area_instructions": common_area_instructions if uses_common_disposal else "N/A"
            },
            "waste_management": {
                "company_name": wm_name,
                "phone": wm_phone,
                "description": wm_description
            }
    }

    st.session_state.progress["trash_completed"] = True
    save_progress(st.session_state.progress)

    # --- Display saved info and uploaded images ---
    if st.session_state.trash_info:
        st.markdown("### ✅ Saved Trash Handling Information")
        for key, value in st.session_state.trash_info.items():
            st.write(f"**{key}**: {value}")

    if st.session_state.trash_images:
        st.write("🖼️ Uploaded Photos")
        for label, image_bytes in st.session_state.trash_images.items():
            if image_bytes:
                st.image(Image.open(io.BytesIO(image_bytes)), caption=label)

def mail_trash_handling():
# Step 1: Input fields
    mail ()
    trash_handling()
    # Step 2: Preview prompt

    # Move this outside the expander
    user_confirmation = st.checkbox("✅ Confirm AI Prompt")
    st.session_state["user_confirmation"] = user_confirmation # store confirmation in session

    st.session_state.progress["level_3_completed"] = True
    save_progress(st.session_state.progress)

    if user_confirmation:
        prompt_emergency = emergency_kit_utilities_runbook_prompt()
        prompt_mail_trash = mail_trash_runbook_prompt()
        st.session_state["prompt_emergency"] = prompt_emergency
        st.session_state["prompt_mail_trash"] = prompt_mail_trash
    else:
        st.session_state["prompt_emergency"] = None
        st.session_state["prompt_mail_trash"] = None

# Show prompt in expander
    with st.expander("AI Prompt Preview (Optional)"):
        if st.session_state.get("prompt_emergency"):
            st.markdown("#### 🆘 Emergency + Utilities Prompt")
            st.code(st.session_state["prompt_emergency"], language="markdown")
        if st.session_state.get("prompt_mail_trash"):
            st.markdown("#### 📬 Mail + Trash Prompt")
            st.code(st.session_state["prompt_mail_trash"], language="markdown")

    # Step 3: Generate runbook using reusable function
   # st.write("Next, click the button to generate your personalized utilities emergency runbook document:")

    # st.markdown("### 🧪 Debug Info")

    # st.write("🔑 **API Key Loaded:**", "✅ Yes" if os.getenv("MISTRAL_TOKEN") else "❌ No")

    # st.write("✅ **User Confirmed Prompt:**", st.session_state.get("user_confirmation", False))

    # st.write("📄 **Emergency Prompt Exists:**", "✅ Yes" if st.session_state.get("prompt_emergency") else "❌ No")
    # st.code(st.session_state.get("prompt_emergency", "⚠️ Emergency prompt not generated."), language="markdown")

    # st.write("📬 **Mail & Trash Prompt Exists:**", "✅ Yes" if st.session_state.get("prompt_mail_trash") else "❌ No")
    # st.code(st.session_state.get("prompt_mail_trash", "⚠️ Mail/Trash prompt not generated."), language="markdown")

    generate_runbook_from_prompt_split(
        prompt_emergency=st.session_state.get("prompt_emergency", ""),
        prompt_mail_trash=st.session_state.get("prompt_mail_trash", ""),
        api_key=os.getenv("MISTRAL_TOKEN"),
        button_text="Complete Level 3 Mission",
        doc_heading="Home Emergency Runbook for Cartakers and Guests",
        doc_filename="home_runbook_cartakers.docx"
    )
##### Level 4 - Home Security and Services

def home_security():
    st.write("💝 Security-Conscious")

    # Initialize session state
    if 'home_security_info' not in st.session_state:
        st.session_state.home_security_info = {}

    with st.expander("Home Security System (if applicable)", expanded=True):
        st.markdown("##### Home Security and Privacy Info")
        home_security_applicable = st.checkbox("Are you home security and privacy conscious?")

        if home_security_applicable:
            st.session_state.home_security_info['home_security_applicable'] = True

            home_security_comp_name = st.text_input("Name of the home security company")
            if home_security_comp_name:
                st.session_state.home_security_info['home_security_comp_name'] = home_security_comp_name

            home_security_comp_num = st.text_input("Contact number for the home security company")
            if home_security_comp_num:
                st.session_state.home_security_info['home_security_comp_num'] = home_security_comp_num

            arm_disarm_instructions = st.text_area(
                "Instructions to arm and disarm the home security system",
                placeholder="E.g. Shared with you through secure text message or shared password manager link"
            )
            if arm_disarm_instructions:
                st.session_state.home_security_info['arm_disarm_instructions'] = arm_disarm_instructions

            security_alert_steps = st.text_area(
                "Steps to follow if a security alert is triggered",
                placeholder="E.g. Check monitor, call security company"
            )
            if security_alert_steps:
                st.session_state.home_security_info['security_alert_steps'] = security_alert_steps

            indoor_cameras = st.text_area(
                "Are there any indoor cameras or monitoring systems in place, and how are they activated?"
            )
            if indoor_cameras:
                st.session_state.home_security_info['indoor_cameras'] = indoor_cameras

            access_emergency = st.text_area(
                "Access instructions for emergencies or lockouts, and where those instructions are stored"
            )
            if access_emergency:
                st.session_state.home_security_info['access_emergency'] = access_emergency

            wifi_network_name = st.text_input(
                "Where is the Wi-Fi network name and password typically stored?"
            )
            if wifi_network_name:
                st.session_state.home_security_info['wifi_network_location'] = wifi_network_name

            wifi_guests = st.text_input(
                "Is there a specific Wi-Fi network guests should use? If yes, how is the password shared?"
            )
            if wifi_guests:
                st.session_state.home_security_info['wifi_guests'] = wifi_guests

            landline_voip = st.text_area(
                "Are there any home phones? If yes, how should calls be handled? Who should be contacted for any home phone issues?"
            )
            if landline_voip:
                st.session_state.home_security_info['landline_voip'] = landline_voip

        else:
            st.info("🔒 You indicated home security is not applicable.")
            st.session_state.home_security_info = {"home_security_applicable": False}
    
    # --- Save Button ---
    if st.button("💾 Security-Conscious Info"):
        st.session_state["home_security_saved"] = True
        st.success("✅ Home Security and Privacy information saved successfully!")
    
def convenience_seeker():
    st.write("🧼 Quality-Oriented Household Services")

    # Initialize in session state
    if 'convenience_seeker_info' not in st.session_state:
        st.session_state.convenience_seeker_info = {}

    with st.expander("Home Quality-Oriented (if applicable)", expanded=True):
        st.markdown("##### Services You Invest In")
        
        options = st.multiselect(
            "As someone who wants their home and garden to be well-maintained and is willing to invest in professional help, what services do you pay for?",
            ["Cleaning", "Gardening/Landscape", "Pool Maintenance"]
        )
        st.session_state.convenience_seeker_info['convenience_seeker_options'] = options

        # --- Cleaning Service ---
        if "Cleaning" in options:
            st.subheader("🧹 Cleaning Service Info")
            st.session_state.convenience_seeker_info['cleaning_name'] = st.text_input("Cleaning Company Name")
            st.session_state.convenience_seeker_info['cleaning_number'] = st.text_input("Cleaning Company Phone Number")
            st.session_state.convenience_seeker_info['cleaning_schedule'] = st.text_input("Cleaning Schedule")
            st.session_state.convenience_seeker_info['cleaning_access'] = st.text_input("Access Method for Cleaners")
            st.session_state.convenience_seeker_info['cleaning_finish_steps'] = st.text_area("Post-Cleaning Procedures")
            st.session_state.convenience_seeker_info['cleaning_identity_confirmation'] = st.text_area("Cleaning Crew Identity Verification")

        # --- Gardening/Landscape Service ---
        if "Gardening/Landscape" in options:
            st.subheader("🌿 Gardening/Landscape Service Info")
            st.session_state.convenience_seeker_info['gardening_name'] = st.text_input("Gardening Company Name")
            st.session_state.convenience_seeker_info['gardening_number'] = st.text_input("Gardening Company Phone Number")
            st.session_state.convenience_seeker_info['gardening_schedule'] = st.text_input("Gardening Schedule")
            st.session_state.convenience_seeker_info['gardening_access'] = st.text_input("Access Method for Gardeners")
            st.session_state.convenience_seeker_info['gardening_finish_steps'] = st.text_area("Post-Gardening Procedures")
            st.session_state.convenience_seeker_info['gardening_identity_confirmation'] = st.text_area("Gardening Crew Identity Verification")

        # --- Pool Maintenance Service ---
        if "Pool Maintenance" in options:
            st.subheader("🏊 Pool Maintenance Info")
            st.session_state.convenience_seeker_info['pool_name'] = st.text_input("Pool Maintenance Company Name")
            st.session_state.convenience_seeker_info['pool_number'] = st.text_input("Pool Company Phone Number")
            st.session_state.convenience_seeker_info['pool_schedule'] = st.text_input("Pool Maintenance Schedule")
            st.session_state.convenience_seeker_info['pool_access'] = st.text_input("Access Method for Pool Techs")
            st.session_state.convenience_seeker_info['pool_finish_steps'] = st.text_area("Post-Maintenance Procedures")
            st.session_state.convenience_seeker_info['pool_identity_confirmation'] = st.text_area("Pool Crew Identity Verification")
        
        # --- Save Button ---
    if st.button("💾 Quality-Oriented Household Services Info"):
        st.session_state["convenience_seeker_saved"] = True
        st.success("✅ Services you invest in information saved successfully!")


def rent_own():
    st.write("🏠 Home Ownership Status")

    if "rent_own_info" not in st.session_state:
        st.session_state.rent_own_info = {}

    housing_status = st.selectbox(
        "Do you rent or own your home?",
        ("Select an option", "Rent", "Own")
    )

    st.session_state.rent_own_info["housing_status"] = housing_status

    if housing_status == "Rent":
        st.subheader("🏢 Property Management Info")

        st.session_state.rent_own_info["property_management_name"] = st.text_input("Company Name")
        st.session_state.rent_own_info["property_management_number"] = st.text_input("Company Phone Number")
        st.session_state.rent_own_info["property_management_email"] = st.text_input("Company Email")
        st.session_state.rent_own_info["property_management_description"] = st.text_area(
            "When to Contact", placeholder="E.g. Roof issues, leaking pipe, parking, etc."
        )

    elif housing_status == "Own":
        st.subheader("🧰 Homeowner Contacts")

        homeowner_contacts_options = st.multiselect(
            "Which service contacts are applicable?",
            ["Handyman/Contractor", "Electrician", "Exterminator", "Plumber", "HOA"]
        )

        st.session_state.rent_own_info["homeowner_contacts_options"] = homeowner_contacts_options

        # Utility function for section layout
        def contact_section(role):
            st.write(f"### {role}")
            name = st.text_input(f"{role} Name")
            number = st.text_input(f"{role} Phone Number")
            description = st.text_area(f"When to Contact {role}?")
            if name: st.session_state.rent_own_info[f"{role.lower()}_name"] = name
            if number: st.session_state.rent_own_info[f"{role.lower()}_number"] = number
            if description: st.session_state.rent_own_info[f"{role.lower()}_description"] = description

        if "Handyman/Contractor" in homeowner_contacts_options:
            contact_section("Handyman")

        if "Electrician" in homeowner_contacts_options:
            contact_section("Electrician")

        if "Exterminator" in homeowner_contacts_options:
            contact_section("Exterminator")

        if "Plumber" in homeowner_contacts_options:
            contact_section("Plumber")

        if "HOA" in homeowner_contacts_options:
            st.write("🏘️ HOA / Property Management")

            st.session_state.rent_own_info["property_management_name"] = st.text_input("Company Name (HOA)")
            st.session_state.rent_own_info["property_management_number"] = st.text_input("Phone Number (HOA)")
            st.session_state.rent_own_info["property_management_email"] = st.text_input("Email (HOA)")
            st.session_state.rent_own_info["property_management_description"] = st.text_area(
                "When to Contact (HOA)",
                placeholder="E.g. roof issues, bylaws, common areas, etc."
            )
        # --- Save Button ---
    if st.button("💾 Save Housing Status & Contacts Info"):
        st.session_state["rent_own_saved"] = True
        st.success("✅ Housing Status and contact information saved successfully!")


def security_convenience_ownership():
    st.subheader("Level 4: Home Security, Privacy, Quality-Orientation, and Support")
    # Step 1: User Input
    home_security()
    convenience_seeker()
    rent_own()
    
    # Step 2: Preview prompt

    # Move this outside the expander
    user_confirmation = st.checkbox("✅ Confirm AI Prompt")
    st.session_state["user_confirmation"] = user_confirmation # store confirmation in session

    st.session_state.progress["level_4_completed"] = True
    save_progress(st.session_state.progress)

    if user_confirmation:
        prompt_emergency = emergency_kit_utilities_runbook_prompt()
        prompt_mail_trash = mail_trash_runbook_prompt()
        prompt_home_caretaker = home_caretaker_runbook_prompt()
        st.session_state["prompt_emergency"] = prompt_emergency
        st.session_state["prompt_mail_trash"] = prompt_mail_trash
        st.session_state["prompt_home_caretaker"]= prompt_home_caretaker
    else:
        st.session_state["prompt_emergency"] = None
        st.session_state["prompt_mail_trash"] = None
        st.session_state["prompt_home_caretaker"]= None

# Show prompt in expander
    with st.expander("AI Prompt Preview (Optional)"):
        if st.session_state.get("prompt_emergency"):
            st.markdown("#### 🆘 Emergency + Utilities Prompt")
            st.code(st.session_state["prompt_emergency"], language="markdown")
        if st.session_state.get("prompt_mail_trash"):
            st.markdown("#### 📬 Mail + Trash Prompt")
            st.code(st.session_state["prompt_mail_trash"], language="markdown")
        if st.session_state.get("prompt_home_caretaker"):
            st.markdown("#### 💝 Home Protection + Services Prompt")
            st.code(st.session_state["prompt_home_caretaker"], language="markdown")

    # Step 3: Generate runbook using reusable function
   # st.write("Next, click the button to generate your personalized utilities emergency runbook document:")

    # st.markdown("### 🧪 Debug Info")

    # st.write("🔑 **API Key Loaded:**", "✅ Yes" if os.getenv("MISTRAL_TOKEN") else "❌ No")

    # st.write("✅ **User Confirmed Prompt:**", st.session_state.get("user_confirmation", False))

    # st.write("📄 **Emergency Prompt Exists:**", "✅ Yes" if st.session_state.get("prompt_emergency") else "❌ No")
    # st.code(st.session_state.get("prompt_emergency", "⚠️ Emergency prompt not generated."), language="markdown")

    # st.write("📬 **Mail & Trash Prompt Exists:**", "✅ Yes" if st.session_state.get("prompt_mail_trash") else "❌ No")
    # st.code(st.session_state.get("prompt_mail_trash", "⚠️ Mail/Trash prompt not generated."), language="markdown")

    generate_runbook_from_multiple_prompts(
        prompts=[
            st.session_state.get("prompt_emergency", ""),
            st.session_state.get("prompt_mail_trash", ""),
            st.session_state.get("prompt_home_caretaker", "")
        ],
        api_key=os.getenv("MISTRAL_TOKEN"),
        button_text="Complete Level 4 Mission",
        doc_heading="Comprehensive Housekeeping Runbook",
        doc_filename="housekeeping_runbook.docx"
    )
##### Level 5 - Emergency Kit Critical Documents

def emergency_kit_critical_documents():
    # Define categories and the corresponding documents
    documents = {
        'Identification Documents': [
            'Government-issued ID (Driver’s license, state ID, or passport)',
            'Social Security Card',
            'Birth Certificates',
            'Marriage/Divorce Certificates',
            'Citizenship/Immigration Documents'
        ],
        'Health and Medical Documents': [
            'Health Insurance Cards',
            'Prescription Medications List',
            'Vaccination Records',
            'Emergency Medical Information',
            'Medical Power of Attorney'
        ],
        'Financial Documents': [
            'Bank Account Information',
            'Credit Cards/Debit Cards',
            'Checkbook',
            'Tax Returns (Last Year’s)',
            'Insurance Policies (Auto, Health, Home, Life, etc.)',
            'Investment Documents'
        ],
        'Homeownership or Rental Documents': [
            'Deed or Lease Agreement',
            'Mortgage or Rent Payment Records',
            'Home Insurance Policy'
        ],
        'Legal Documents': [
            'Will or Living Will',
            'Power of Attorney',
            'Property Title and Vehicle Titles',
            'Child Custody or Adoption Papers'
        ],
        'Emergency Contact Information': [
            'Contact List',
            'Emergency Plan'
        ],
        'Travel Documents': [
            'Passport',
            'Travel Itinerary'
        ],
        'Educational Documents': [
            'School Records',
            'Diplomas and Degrees',
            'Certificates and Licenses'
        ],
        'Digital Backup': [
            'USB Flash Drive or External Hard Drive',
            'Cloud Storage'
        ],
        'Miscellaneous Documents': [
            'Pet Records',
            'Photos of Important Belongings',
            'Bankruptcy or Legal Filings'
        ]
    }

    # Initialize session state for storing selections if not already initialized
    if "selected_documents" not in st.session_state:
        st.session_state.selected_documents = {}

    # Step 1: Prompt the user to select a category
    selected_category = st.selectbox(
        'Select a document category to view:',
        options=list(documents.keys())
    )
    
    # Step 2: Display a multi-select based on the selected category
    if selected_category:
        st.write(f'You selected the category: **{selected_category}**')
        selected_docs_for_category = st.multiselect(
            f'Select documents from the **{selected_category}** category:',
            options=documents[selected_category],
            default=st.session_state.selected_documents.get(selected_category, [])
        )
        
        # Step 3: Save the selected documents to session state for the chosen category
        if selected_docs_for_category:
            st.session_state.selected_documents[selected_category] = selected_docs_for_category
        
        # Display the current selections for that category
        st.write(f'### Documents selected in **{selected_category}**:')
        for doc in selected_docs_for_category:
            st.write(f' - {doc}')
    
    # Step 4: Option to add more categories or finalize
    add_more = st.button('Add more categories')
    if add_more:
        st.write("Feel free to select another category.")
    
    # Finalize button to save all selections
    finalize = st.button('Finalize and Save All Selections')
    
    if finalize:
        st.write('### All Selections:')
        for category, docs in st.session_state.selected_documents.items():
            st.write(f'**{category}:**')
            for doc in docs:
                st.write(f' - {doc}')
        st.session_state.finalized = True
        st.write("All your selections have been saved!")

    # Show saved selections
    if "finalized" in st.session_state and st.session_state.finalized:
        st.write("### Your final saved selections:")
        for category, docs in st.session_state.selected_documents.items():
            st.write(f'**{category}:**')
            for doc in docs:
                st.write(f' - {doc}')

# Call the function to display the multiselect in the Streamlit app






### Call App Functions
if __name__ == "__main__":
    main()