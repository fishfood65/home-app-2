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

    elif section == "Level 5":
        st.subheader("🚀 Level 5 Launch")

    elif section == "Bonus Level":
        st.subheader("🎁 Bonus Level Content")

    # Optional: Reset button
    if st.sidebar.button("🔄 Reset Progress"):
        st.session_state.progress = {}
        save_progress({})
        st.experimental_rerun()

#### Reusable Functions to Generate and Format Runbooks #####
def format_output_for_docx(output: str) -> str:
    """Formats markdown-like output to docx-friendly text."""
    if not output:
        return ""
    formatted_text = re.sub(r"^## (.*)", r"\n\n\1\n", output, flags=re.MULTILINE)
    formatted_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", formatted_text)
    formatted_text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", formatted_text)
    return formatted_text

def generate_runbook_from_prompt(
    prompt: str,
    api_key: str,
    button_text: str,
    doc_heading: str,
    doc_filename: str
):
    """
    Reusable Streamlit function to handle LLM completion and export a DOCX file.
    """
    unique_key = f"{button_text.lower().replace(' ', '_')}_button"
    clicked = st.button(button_text, key=unique_key)

    # Debug section
    #st.write("🔍 Debug info:")
    #st.write("- Button clicked:", clicked)
    #st.write("- user_confirmation:", st.session_state.get("user_confirmation"))
    #st.write("- Prompt present:", bool(prompt))
    #st.write("📋 Session State:", dict(st.session_state))

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

                formatted_output = format_output_for_docx(output)

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
                st.error(f"❌ Failed to generate runbook: {str(e)}")

        else:
            st.warning("⚠️ Prompt not confirmed or missing.")

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

###### Main Functions that comprise of the Levels

### Leve 1 - Home

def home_debug():

    st.write("🟡 About to render runbook button")

    generate_runbook_from_prompt(
        prompt=st.session_state.get("generated_prompt", ""),
        api_key=os.getenv("MISTRAL_TOKEN"),
        button_text="Complete Level 1 Mission",
        doc_heading="Home Utilities Emergency Runbook",
        doc_filename="home_utilities_emergency.docx"
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

        kitchen_bin_location = st.text_area(
            "Kitchen Trash Bin Location", 
            placeholder="E.g. Under the kitchen sink"
        )

        bathroom_bin_location = st.text_area(
            "Bathroom Trash Bin Location", 
            placeholder="E.g. Near the toilet"
        )

        trash_bag_type = st.text_area(
            "Trash Bag Type & Location", 
            placeholder="E.g. Black bags in pantry"
        )

        emptying_schedule = st.text_area(
            "Emptying Schedule", 
            placeholder="E.g. Empty every night"
        )

        replacement_instructions = st.text_area(
            "Replacing Trash Bags", 
            placeholder="E.g. Replace bag when full"
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
            bool(kitchen_bin_location),
            bool(bathroom_bin_location),
            bool(trash_bag_type),
            bool(emptying_schedule),
            bool(replacement_instructions),
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
                "kitchen_bin_location": kitchen_bin_location,
                "bathroom_bin_location": bathroom_bin_location,
                "trash_bag_type": trash_bag_type,
                "emptying_schedule": emptying_schedule,
                "replacement_instructions": replacement_instructions
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

    st.success("All trash handling instructions saved successfully!")

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

    if user_confirmation:
        prompt = emergency_mail_trash_runbook_prompt()
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
        button_text="Complete Level 3 Mission",
        doc_heading="Home Emergency Runbook for Cartakers and Guests",
        doc_filename="home_runbook_cartakers.docx"
    )

### Call App Functions
if __name__ == "__main__":
    main()