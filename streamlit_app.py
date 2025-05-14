import streamlit as st
from mistralai import Mistral
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

# Run the app if this script is executed
#if __name__ == "__main__":
#    main()

# Main entry point of the app
def main():
    # Initialize session state
    if 'home_info' not in st.session_state:
        st.session_state.home_info = {}

    # Sidebar navigation
    section = st.sidebar.radio(
        "Choose a Level:",
        ("Level 1", "Level 2", "Level 3")
    )

    # Always allow user to fill out Home Info
    if section == "Level 1":
        home()

    # Only allow access to other sections if home info is saved
    elif section in ("Level 2", "Level 3"):
        if not st.session_state.home_info:
            st.warning("⚠️ Please complete the Level 1 fiwst.")
            home()
        else:
            if section == "Level 2":
                mail_trash_handling()
            elif section == "Level 3":
                security_convenience_ownership()

def home():
    st.subheader("Level 1: 🏡 Home")
    st.write("Let's gather some information. Please enter your details:")

# Get user Input to enter input
    city = st.text_input("Enter Your City:")
    zip_code = st.text_input("Enter Your Zip Code:")
    internet_provider = st.text_input("Enter Your Internet Provider Name:")

# Save user input into home_info
    if st.button(" Click to Save"):
        if city and zip_code and internet_provider:
         st.session_state.home_info = {
            "City": city,
            "Zip Code": zip_code,
            "Internet Provider Name": internet_provider,
            }
        st.success("✅ Home information saved successfully!")
    else:
        st.error("❌ Please fill in all fields before saving.")

    # Display the saved user information
    if st.session_state.home_info:
        with st.expander("Saved home Information", expanded=True):
            for key, value in st.session_state.home_info.items():
                st.write(f"{key}: {value}")
    
    with st.expander("Confirm AI Prompt Preview by Selecting the button inside"):
        user_confirmation = st.checkbox("Show AI Prompt")
        if user_confirmation:
            prompt = f"""
            Compose a comprehensive, step-by-step emergency run book for residents of City:{city} Zip Code:{zip_code} with Internet Provider:{internet_provider}, with a focus on guiding users through power outages, gas leaks, water leaks/outages, and internet service disruptions. Include the following details for each utility and service provider:
            1. **Electricity (<electricity_provider_name>):**
            - Description of the company and services
            - Customer service number and address
            - Official website
            - Emergency contact information for power outages and gas leaks
            - Step-by-step guide on what to do during a power outage, including when and how to report it

            2. **Natural Gas (<natural_gas_provider_name>):**
            - Description of the company and services
            - Customer service number and address
            - Official website
            - Emergency contact information for gas-related issues
            - Step-by-step guide on what to do if you suspect a gas leak

            3. **Water (<water_provider_name>):**
            - Description of the company and services
            - Customer service number and address
            - Official website
            - Emergency contact information for water outages and leaks
            - Step-by-step guide on what to do during a water outage or leak

            4. **Internet (<internet_provider_name>):**
            - Description of the company and services
            - Customer service number and address
            - Official website
            - Emergency contact information for internet outages
            - Step-by-step guide on what to do during an internet outage

            Ensure the run book is well-structured, easy to understand, and includes relevant links to official websites and resources. Format the response in a clear, step-by-step manner, with headings and bullet points for easy navigation.
                
                Please replace <city>, <zip_code>, <internet_provider> and placeholders like <electricity_provider_name>, etc., with the actual information for the specified city and zip code. 
                """
            st.code(prompt)

    # Generate comprehensive output using Mistral API
    st.write ("Next, Click the button to generate your persoanlized utlities emergency run book document")

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

    if st.button("Complete Level 1 Mission"):
        if user_confirmation:
            # Use Mistral for model inference
            client = Mistral(api_key=api_key)
            
            # Define the prompt as a "chat" message format
            completion = client.chat.complete(
                model="mistral-small-latest",  # Specify the model ID
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
            
            st.success("Emergency utilities run book generated successfully! Mission Accomplished.")
            st.write(output_text)

            # Create a DOCX file from the output text
            doc = Document()
            doc.add_heading('Home Utilities Emergency Runbook', 0)
            
            # Process and add formatted output to the document
            # Example: preserve line breaks and formatting in output
            formatted_output = process_output_for_formatting(output)
            doc.add_paragraph(formatted_output)
        

            # Save DOCX to a temporary file
            doc_filename = "home_utilities_emergency.docx"
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

def mail_trash_handling():
    st.subheader("Level 2: Mail and Trash Handling")
    mail ()
    trash_handling()

    with st.expander("Confirm Level 2 AI Prompt Preview by Selecting the button inside"):
        user_confirmation = st.checkbox("Show Level 2 AI Prompt")
        if user_confirmation:
            prompt = f"""
            You are a helpful assistant creating an **Emergency Manual** for a household located in a city: {st.session_state.home_info.get("City", "Unknown City")} and Zip Code: {st.session_state.home_info.get("Zip Code", "00000")}.  This manual is for residents or house sitters to use during emergencies, with clear, calm, and step-by-step guidance.

            The home has the following setup:
            - **Internet Provider**: {st.session_state.home_info.get("Internet Provider Name", "N/A")}
            - **Mailbox Location**: {st.session_state.mail_info.get("Mailbox Location", "N/A")}
            - **Mailbox Key Instructions**: {st.session_state.mail_info.get("Mailbox Key", "N/A")}
            - **Mail Pickup Schedule**: {st.session_state.mail_info.get("Pick-Up Schedule", "N/A")}
            - **What to Do with Mail**: {st.session_state.mail_info.get("What to Do with the Mail", "N/A")}
            - **What to Do with Packages**: {st.session_state.mail_info.get("Packages", "N/A")}

            **Trash Handling Setup**:
            - Kitchen Bin: {st.session_state.trash_info.get("Kitchen Trash Bin Location", "N/A")}
            - Bathroom Bin: {st.session_state.trash_info.get("Bathroom Trash Bin Location", "N/A")}
            - Trash Bags: {st.session_state.trash_info.get("Trash Bag Type & Storage", "N/A")}
            - Emptying Schedule: {st.session_state.trash_info.get("Emptying Schedule", "N/A")}
            - Replacement Instructions: {st.session_state.trash_info.get("Replacing Trash Bags", "N/A")}
            - Trash Bin Destination: {st.session_state.trash_info.get("Where to Empty Trash Bins", "N/A")}
            - Bin Description: {st.session_state.trash_info.get("Outdoor Bin Description", "N/A")}
            - Outdoor Bin Location Instructions: {st.session_state.trash_info.get("Outdoor Bin Location Instructions", "N/A")}
            - Garbage Pickup Day/Time: {st.session_state.trash_info.get("Garbage Pickup Day", "N/A")} / {st.session_state.trash_info.get("Garbage Pickup Time", "N/A")}
            - Recycling Pickup Day/Time: {st.session_state.trash_info.get("Recycling Pickup Day", "N/A")} / {st.session_state.trash_info.get("Recycling Pickup Time", "N/A")}
            - Bin Placement Instructions: {st.session_state.trash_info.get("Outdoor Bin Pickup/Return Instructions", "N/A")}
            - Composting Used: {st.session_state.trash_info.get("Composting Used", "No")}
            - Compost Instructions: {st.session_state.trash_info.get("Compost Instructions", "N/A")}
            - Common Disposal Area: {st.session_state.trash_info.get("Uses Common Disposal Area", "No")}
            - Common Area Instructions: {st.session_state.trash_info.get("Common Disposal Instructions", "N/A")}

            **Waste Management Company Contact**:
            - Name: {st.session_state.trash_info.get("Waste Management Contact Name", "N/A")}
            - Phone: {st.session_state.trash_info.get("Waste Management Contact Phone", "N/A")}
            - When to Call: {st.session_state.trash_info.get("Waste Management Contact Description", "N/A")}

            Now, generate a **step-by-step emergency manual** for the following situations:

            ---

            ### ⚡ ** Power Outages (<electricity_provider_name>):**
            - Description of the company and services
            - Customer service number and address
            - Official website
            - What to check
            - What to unplug
            - Where flashlights or backup supplies might be located

            ---

            ### 🔥 ** Gas Leaks(<natural_gas_provider_name>):**
            - Warning signs
            - Immediate actions to take (e.g., evacuate, don’t use electrical switches)
            - How to shut off the gas (include a general step if specific not available)
            - Emergency contact for local gas company or 911

            ---

            ### 💧 ** Water Leaks & Outages(<water_provider_name>):**
            - Description of the company and services
            - Customer service number and address
            - Official website
            - Emergency contact information for water outages and leaks
            - Step-by-step guide on what to do during a water outage or leak 
            - Common leak points to check
            - Shut-off valve location (include placeholder if not supplied)
            - Water company emergency line (Insert `<water_provider_name>` placeholder)

            ---

            ### 🌐 Internet Disruptions
            - How to reboot router/modem
            - What to check first (e.g., cables, outage site)
            - Internet provider: {st.session_state.home_info.get("Internet Provider Name", "N/A")}
            - Description of the company and services
            - Customer service number and address
            - Official website
            - Emergency contact information for internet outages
            - Step-by-step guide on what to do during an internet outage

            ---

            ### 📬 Mail Handling
            - Mailbox location & key access
            - Pickup schedule
            - What to do with mail and packages if resident is away

            ---

            ### 🗑️ Garbage Disposal
            - Indoor trash process
            - Outdoor bin instructions and schedule
            - Recycling and composting notes
            - What to do in case of missed pickup
            - Waste Management Contact Info

            ---

            ### 📎 Format
            Organize the manual using **headings and bullet points**. Keep instructions **clear, calm, and easy to follow** for someone unfamiliar with the home.

             Please replace placeholders like <electricity_provider_name>, etc., with the actual information for the specified city and zip code. 

            Please begin the emergency manual now.
            """
            st.code(prompt)

    # Generate comprehensive output using Mistral API
    st.write ("Next, Click the button to generate your personalized emergency run book document")

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

    if st.button("Complete Level 2 Mission"):
        if user_confirmation:
            # Use Mistral for model inference
            client = Mistral(api_key=api_key)
            
            # Define the prompt as a "chat" message format
            completion = client.chat.complete(
                model="mistral-small-latest",  # Specify the model ID
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
            
            st.success("Emergency run book generated successfully! Mission Accomplished.")
            st.write(output_text)

            # Create a DOCX file from the output text
            doc = Document()
            doc.add_heading('Home Emergency Runbook', 0)
            
            # Process and add formatted output to the document
            # Example: preserve line breaks and formatting in output
            formatted_output = process_output_for_formatting(output)
            doc.add_paragraph(formatted_output)
        

            # Save DOCX to a temporary file
            doc_filename = "home_emergency.docx"
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

def mail():
    st.write("Mail Handling Instructions")

    # Initialize mail_info in session state
    if 'mail_info' not in st.session_state:
        st.session_state.mail_info = {}

    with st.expander("Mail Handling", expanded=True):
        mailbox_location = st.text_area(
            "Mailbox Location",
            key="mailbox_location",
            placeholder="The mailbox is located [describe location clearly — e.g., \"at the end of the driveway on the left side\" or \"in the lobby, box #204\""
        )
        if mailbox_location:
            st.progress(20)  # Progress bar for Mailbox Location_location

        mailbox_key = st.text_area(
            "Mailbox Key (Optional)",
            key="mailbox_key",
            placeholder="The key is located [e.g., “on the key hook next to the fridge,” or “inside the top drawer in the entryway table”]. It’s labeled Mailbox for easy identification."
        )
        if mailbox_key:
            st.progress(40)  # Progress bar for Mailbox Key

        pick_up_schedule = st.text_area(
            "Mail Pick-Up Schedule",
            key="pick_up_schedule",
            placeholder="Please check the mail [e.g., “daily,” “every other day,” or “on Mondays and Thursdays”]. If it looks like there's a lot of mail piling up, feel free to pick it up more often."
        )
        if pick_up_schedule:
            st.progress(60)  # Progress bar for Pick-Up Schedule

        what_to_do_with_mail = st.text_area(
            "What to do with the Mail",
            key="what_to_do_with_mail",
            placeholder="Place all mail in the designated spot: [e.g., “the tray on the kitchen counter,” or “the mail basket by the front door”].  If you notice anything urgent (like official notices or something from a bank), feel free to text me a photo just in case."
        )
        if what_to_do_with_mail:
            st.progress(80)  # Progress bar for What to Do with the Mail

        What_to_do_with_packages = st.text_area(
            "Packages",
            key="packages",
            placeholder="If a package arrives and it doesn't fit in the mailbox: Check by the front door, porch, or behind the side gate (sometimes deliveries are left there).  Bring it inside and place it [e.g., “on the dining table” or “inside the entryway closet”]"
        )
        if What_to_do_with_packages:
            st.progress(100)  # Progress bar for Packages

        # Save user input into mail_info
        if st.button("Mail Handling 100% Complete. Click to Save"):
            st.session_state.mail_info = {
                "Mailbox Location": mailbox_location,
                "Mailbox Key": mailbox_key,
                "Pick-Up Schedule": pick_up_schedule,
                "What to Do with the Mail": what_to_do_with_mail,
                "Packages": What_to_do_with_packages
            }
            st.success("User information saved successfully!")

    # Display the saved user information
    st.write("Saved Mail Handing Information")
    if st.session_state.mail_info:
        with st.expander("Saved User Information", expanded=True):
            for key, value in st.session_state.mail_info.items():
                st.write(f"{key}: {value}")
    else:
        st.write("No user information saved yet.")

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
        progress = 0
        increment = 20
        bar1 = st.progress(progress)

        kitchen_bin_location = st.text_area("Kitchen Trash Bin Location", placeholder="E.g. Under the kitchen sink")
        if kitchen_bin_location: progress += increment; bar1.progress(progress)

        bathroom_bin_location = st.text_area("Bathroom Trash Bin Location", placeholder="E.g. Near the toilet")
        if bathroom_bin_location: progress += increment; bar1.progress(progress)

        trash_bag_type = st.text_area("Trash Bag Type & Location", placeholder="E.g. Black bags in pantry")
        if trash_bag_type: progress += increment; bar1.progress(progress)

        emptying_schedule = st.text_area("Emptying Schedule", placeholder="E.g. Empty every night")
        if emptying_schedule: progress += increment; bar1.progress(progress)

        replacement_instructions = st.text_area("Replacing Trash Bags", placeholder="E.g. Replace bag when full")
        if replacement_instructions: progress += increment; bar1.progress(progress)

    # --- Outdoor Bin Info ---
    with st.expander("Outdoor Bin Details", expanded=True):
        st.markdown("##### Outdoor Bin Handling Details")
        progress = 0
        increment = 33
        bar2 = st.progress(progress)

        bin_destination = st.text_area("Where to Empty the Trash Bins", placeholder="E.g. By the curb on pickup day")
        if bin_destination: progress += increment; bar2.progress(progress)

        bin_description = st.text_area("What the Outdoor Trash Bins Look Like", placeholder="E.g. Green with lid")
        if bin_description: progress += increment; bar2.progress(progress)

        bin_location_specifics = st.text_area("Specific Location or Instructions for Outdoor Bins", placeholder="E.g. Next to side gate")
        if bin_location_specifics: progress += increment; bar2.progress(progress)

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
        progress = 0
        increment = 25
        bar3 = st.progress(progress)

        trash_day = st.selectbox("Garbage Pickup Day", days)
        if trash_day: progress += increment; bar3.progress(progress)

        trash_time = st.selectbox("Garbage Pickup Time", times)
        if trash_time: progress += increment; bar3.progress(progress)

        recycling_day = st.selectbox("Recycling Pickup Day", days)
        if recycling_day: progress += increment; bar3.progress(progress)

        recycling_time = st.selectbox("Recycling Pickup Time", times)
        if recycling_time: progress += increment; bar3.progress(progress)

        bin_handling_instructions = st.text_area("Instructions for Placing and Returning Outdoor Bins")

    # --- Common Disposal Area ---
    with st.expander("Common Disposal Area (if applicable)", expanded=True):
        st.markdown("##### Shared disposal area details")
        uses_common_disposal = st.checkbox("Is there a common disposal area?")
        common_area_instructions = ""
        progress = 0
        bar4 = st.progress(progress)

        if uses_common_disposal:
            common_area_instructions = st.text_area("Instructions for Common Disposal Area", placeholder="E.g. Dumpster in alley")
            if common_area_instructions:
                progress += 100
                bar4.progress(progress)
                handle_image("Common Area", "Common Disposal Area")

    # --- Composting ---
    with st.expander("Composting Instructions (if applicable)", expanded=True):
        st.markdown("##### Composting info")
        compost_applicable = st.checkbox("Is composting used?")
        compost_instructions = ""
        progress = 0
        bar5 = st.progress(progress)

        if compost_applicable:
            compost_instructions = st.text_area("Compost Instructions", placeholder="E.g. Put organics in green bin")
            if compost_instructions:
                progress += 100
                bar5.progress(progress)

    # --- Waste Management Contact ---
    with st.expander("Waste Management Contact Info", expanded=True):
        st.markdown("##### Company contact details")
        progress = 0
        increment = 33
        bar6 = st.progress(progress)

        wm_name = st.text_input("Waste Management Company Name", placeholder="E.g. WastePro")
        if wm_name: progress += increment; bar6.progress(progress)

        wm_phone = st.text_input("Contact Phone Number", placeholder="E.g. (123) 456-7890")
        if wm_phone: progress += increment; bar6.progress(progress)

        wm_description = st.text_area("When to Contact", placeholder="E.g. Missed pickup or billing issues")
        if wm_description: progress += increment; bar6.progress(progress)

    # --- Save Button ---
    if st.button("✅ Trash Handling 100% Complete. Click to Save"):
        st.session_state.trash_info = {
            "Kitchen Trash Bin Location": kitchen_bin_location,
            "Bathroom Trash Bin Location": bathroom_bin_location,
            "Trash Bag Type & Storage": trash_bag_type,
            "Emptying Schedule": emptying_schedule,
            "Replacing Trash Bags": replacement_instructions,
            "Where to Empty Trash Bins": bin_destination,
            "Outdoor Bin Description": bin_description,
            "Outdoor Bin Location Instructions": bin_location_specifics,
            "Garbage Pickup Day": trash_day,
            "Garbage Pickup Time": trash_time,
            "Recycling Pickup Day": recycling_day,
            "Recycling Pickup Time": recycling_time,
            "Outdoor Bin Pickup/Return Instructions": bin_handling_instructions,
            "Composting Used": "Yes" if compost_applicable else "No",
            "Compost Instructions": compost_instructions if compost_applicable else "N/A",
            "Uses Common Disposal Area": "Yes" if uses_common_disposal else "No",
            "Common Disposal Instructions": common_area_instructions if uses_common_disposal else "N/A",
            "Waste Management Contact Name": wm_name,
            "Waste Management Contact Phone": wm_phone,
            "Waste Management Contact Description": wm_description
            }
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

def security_convenience_ownership():
    st.subheader("Level 3: Security, Privacy, and Quality-Oriented")
    home_security()
    convenience_seeker()
    rent_own()

def home_security():
    st.write("Security-Conscious")
    # Initialize Security-Conscious in session state
    if 'home_security_info' not in st.session_state:
        st.session_state.home_security_info = {}

    with st.expander("Home Security System (if applicable)", expanded=True):
        st.markdown("##### Home Security and Privacy Info")
        home_security_applicable = st.checkbox("Are you home security and privacy conscious?")
        progress = 0
        increment = 10
        bar7 = st.progress(progress)

        if home_security_applicable:
            st.session_state.home_security_info['home_security_applicable'] = True
            progress += increment; bar7.progress(progress)
            
            home_security_comp_name = st.text_input("Name of the home security company")
            if home_security_comp_name:
                st.session_state.home_security_info['home_security_comp_name'] = home_security_comp_name
                progress += increment; bar7.progress(progress)
            
            home_security_comp_num = st.text_input("Contact number for the home security company")
            if home_security_comp_num:
                st.session_state_home_security_info['home_security_comp_num'] = home_security_comp_num
                progress += increment; bar7.progress(progress)
            
            arm_disarm_instructions = st.text_area("Instructions to arm and disarm the home security are stored", placeholder="E.g. Shared with you through secure text message or shared password manager link")
            if arm_disarm_instructions:
                st.session_state.home_security_info['arm_disarm_instructions'] = arm_disarm_instructions
                progress += increment; bar7.progress(progress)
            
            security_alert_steps = st.text_area("Steps to follow if a security alert is triggered", placeholder="E.g. Check monitor, call security company")
            if security_alert_steps:
                st.session_state.home_security_info['security_alert_steps'] = security_alert_steps
                progress += increment; bar7.progress(progress)

            indoor_cameras = st.text_area("Are there any indoor cameras or monitoring systems in place, and how they might be activated?")
            if indoor_cameras:
                st.session_state.home_security_info['indoor_cameras'] = indoor_cameras
                progress += increment; bar7.progress(progress)

            access_emergency = st.text_area("If there are access instructions available for emergencies or lockouts, and where those instructions are stored (if applicable)")
            if access_emergency:
                st.session_state.home_security_info['access_emergency'] = access_emergency
                progress += increment; bar7.progress(progress)

            wifi_network_name = st.text_input("Where is the Wi-Fi network name and password typically stored in case someone needs it?") 
            if wifi_network_name:
                st.session_state.home_security_info['wifi_network_name'] = wifi_network_name
                progress += increment; bar7.progress(progress)

            wifi_guests = st.text_input("Is there a specific Wi-Fi network guests should use? If yes, how is the password shared?") 
            if wifi_guests:
                st.session_state.home_security_info['wifi_guests'] = wifi_network_name
                progress += increment; bar7.progress(progress)

            landline_voip = st.text_area("Are there any home phones, what are the instructions for when it rings? What provider name and number in case there are issues?")
            if landline_voip:
                st.session_state.home_security_info['landline_voip']=landline_voip
                progress += increment; bar7.progress(progress)
    
def convenience_seeker():
    st.write("Quality-Oriented")
    # Initialize Security-Conscious in session state
    if 'convenience_seeker_info' not in st.session_state:
        st.session_state.convenience_seeker_info = {}

    with st.expander("Home Quality-Orientaed(if applicable)", expanded=True):
        st.markdown("##### Home Quality-Orientaed Info")
        
        convenience_seeker_options = st.multiselect("As Someone who wants their home and garden to be well-maintained and is willing to invest in professional help to achieve this. What are the services you pay for?",
            ["Cleaning", "Gardening/Landscape", "Pool Maintenance"]
            )       
        if 'Cleaning' in convenience_seeker_options:
            st.write("Cleaning Service Info")
            progress = 0
            increment = 16
            bar8 = st.progress(progress)

            cleaning_name = st.text_input("Name of the cleaning company")
            if cleaning_name:
                st.session_state.convenience_seeker_info['cleaning_name'] = cleaning_name
                progress += increment; bar8.progress(progress)
        
            cleaning_number = st.text_input("Number for the cleaning company")
            if cleaning_number:
                st.session_state.convenience_seeker_info['cleaning_number'] = cleaning_number
                progress += increment; bar8.progress(progress)

            cleaning_schedule = st.text_input("Cleaning Schedule")
            if cleaning_schedule:
                st.session_state.convenience_seeker_info['cleaning_number'] = cleaning_schedule
                progress += increment; bar8.progress(progress)

            cleaning_access = st.text_input("How do the cleaners typically gain access to the home (e.g., key, alarm code, security access)?")
            if cleaning_access: 
                st.session_state.convenience_seeker_info['cleaning_access'] = cleaning_access
                progress += increment; bar8.progress(progress)
            
            cleaning_finish_steps = st.text_area("What steps are taken when the cleaning service finishes (e.g., locking up, securing the home)?")
            if cleaning_finish_steps:
                st.session_state.convenience_seeker_info['cleaning_finish_steps']= cleaning_finish_steps
                progress += increment; bar8.progress(progress)
            
            cleaning_identity_confirmation = st.text_area("How do you confirm the identity or legitimacy of the cleaning crew when they arrive (e.g. ID, references)?")
            if cleaning_identity_confirmation:
                st.session_state.convenience_seeker_info['cleaning_identity_confirmation'] =cleaning_identity_confirmation
                progress += increment; bar8.progress(progress)

        if 'Gardening/Landscape' in convenience_seeker_options:
            st.write("Gardening/Landscape Info")
            progress = 0
            increment = 16
            bar9 = st.progress(progress)

            gardening_name = st.text_input("Name of the Gardening/Landscape company")
            if gardening_name:
                st.session_state.convenience_seeker_info['gardening_name'] = gardening_name
                progress += increment; bar9.progress(progress)
        
            gardening_number = st.text_input("Number for the Gardening/Landscape company")
            if gardening_number:
                st.session_state.convenience_seeker_info['gardening_number'] = gardening_number
                progress += increment; bar9.progress(progress)

            gardening_schedule = st.text_input("Gardening/Landscape Schedule")
            if gardening_schedule:
                st.session_state.convenience_seeker_info['gardening_schedule'] = gardening_schedule
                progress += increment; bar9.progress(progress)

            gardening_access = st.text_input("How do the gardeners/landscapers typically gain access to the home (e.g., key, alarm code, security access)?")
            if gardening_access: 
                st.session_state.convenience_seeker_info['gardening_access'] = gardening_access
                progress += increment; bar9.progress(progress)
            
            gardening_finish_steps = st.text_area("What steps are taken when the Gardening/Landscape service finishes (e.g., locking up, securing the home)?")
            if gardening_finish_steps:
                st.session_state.convenience_seeker_info['gardening_finish_steps']= gardening_finish_steps
                progress += increment; bar9.progress(progress)
            
            gardening_identity_confirmation = st.text_area("How do you confirm the identity or legitimacy of the Gardening/Landscape crew when they arrive (e.g. ID, references)?")
            if gardening_identity_confirmation:
                st.session_state.convenience_seeker_info['gardening_identity_confirmation'] =gardening_identity_confirmation
                progress += increment; bar9.progress(progress)

        if 'Pool Maintenance' in convenience_seeker_options:
            st.write("Pool Maintenance Info")
            progress = 0
            increment = 16
            bar10 = st.progress(progress)

            pool_name = st.text_input("Name of the Pool Maintenance company")
            if pool_name:
                st.session_state.convenience_seeker_info['Pool Maintenance_name'] = pool_name
                progress += increment; bar10.progress(progress)
        
            pool_number = st.text_input("Number for the Pool Maintenance company")
            if pool_number:
                st.session_state.convenience_seeker_info['pool_number'] = pool_number
                progress += increment; bar10.progress(progress)

            pool_schedule = st.text_input("Pool Maintenance Schedule")
            if pool_schedule:
                st.session_state.convenience_seeker_info['pool_schedule'] = pool_schedule
                progress += increment; bar10.progress(progress)

            pool_access = st.text_input("How do the pool maintenance service typically gain access to the home (e.g., key, alarm code, security access)?")
            if pool_access: 
                st.session_state.convenience_seeker_info['pool_access'] = pool_access
                progress += increment; bar10.progress(progress)
            
            pool_finish_steps = st.text_area("What steps are taken when the pool maintenance service finishes (e.g., locking up, securing the home)?")
            if pool_finish_steps:
                st.session_state.convenience_seeker_info['pool_finish_steps']= pool_finish_steps
                progress += increment; bar10.progress(progress)
            
            pool_identity_confirmation = st.text_area("How do you confirm the identity or legitimacy of the pool maintenance crew when they arrive (e.g. ID, references)?")
            if pool_identity_confirmation:
                st.session_state.convenience_seeker_info['pool_identity_confirmation'] =pool_identity_confirmation
                progress += increment; bar10.progress(progress)
        
        st.session_state.convenience_seeker_info['convenience_seeker_options'] = convenience_seeker_options

def rent_own():
    st.write("Home Ownership Status")

    # Use st.selectbox to create a dropdown menu for selecting between renting or owning
    housing_status = st.selectbox(
        'Do you rent or own your home?',  # Label for the widget
        ('Select an option', 'Rent', 'Own')  # Options to display in the dropdown menu
    )  

    if housing_status == 'Rent':
            st.write("Property Management Info")
            progress = 0
            increment = 25
            bar11 = st.progress(progress)

            property_management_name = st.text_input("Name of the Property Management Company")
            if property_management_name:
                st.session_state.rent_own_info['property_management_name'] = property_management_name
                progress += increment; bar11.progress(progress)     

            property_management_number = st.text_input("Number for the Property Management Company")
            if property_management_number:
                st.session_state.rent_own_info['property_management_number'] = property_management_number
                progress += increment; bar11.progress(progress)   

            property_management_email = st.text_input("Email for the Property Management Company")
            if property_management_email:
                st.session_state.rent_own_info['property_management_email'] = property_management_email
                progress += increment; bar11.progress(progress) 

            property_management_description = st.text_area("When to Contact Property Management Company", placeholder="E.g. Roof issues, leaking pipe, common areas issues, parking challenges, etc..")
            if property_management_description:
                st.session_state.rent_own_info['property_management_description'] = property_management_description
                progress += increment; bar11.progress(progress)
  
    elif housing_status == 'Own':
            st.write("Homowner Contacts Info")

            homeowner_contacts_options = st.multiselect("Select all the serivce contacts that are applicable.",
            ["Handyman/Contractor", "Electrician", "Exterminator", "Plumber", "HOA", "None" ]
            )     

            if 'Handyman/Contractor' in homeowner_contacts_options:
                st.write("Handyman/Contractor Info")
                progress = 0
                increment = 33
                bar12 = st.progress(progress) 
                
                handyman_name = st.text_input("Name of the Handyman/Contractor")
                if handyman_name:
                    st.session_state.rent_own_info['handyman_name'] = handyman_name
                    progress += increment; bar12.progress(progress)     

                handyman_number = st.text_input("Number for the Handyman/Contractor")
                if handyman_number:
                    st.session_state.rent_own_info['handyman_number'] = handyman_number
                    progress += increment; bar12.progress(progress)   
            
                handyman_description = st.text_area("When to Contact Handyman/Contractor", placeholder="E.g. Door jammed, windows stuck, garbage disposal stopped working etc...")
                if handyman_description: progress += increment; bar12.progress(progress)
           
            if 'Electrician' in homeowner_contacts_options:
                st.write("Electrician")
                progress = 0
                increment = 33
                bar13 = st.progress(progress) 
                
                electrician_name = st.text_input("Name of the Electrician")
                if electrician_name:
                    st.session_state.rent_own_info['electrician_name'] = electrician_name
                    progress += increment; bar13.progress(progress)     

                electrician_number = st.text_input("Number for the Electrician")
                if electrician_number:
                    st.session_state.rent_own_info['electrician_name'] = electrician_number
                    progress += increment; bar13.progress(progress)   
            
                electrician_description = st.text_area("When to contact the Electrician?", placeholder="E.g. Heater not working, A/C not working, Electrical outlets stopped workingetc...")
                if electrician_description: progress += increment; bar13.progress(progress)

            if 'Exterminator' in homeowner_contacts_options:
                st.write("Exterminator")
                progress = 0
                increment = 33
                bar14 = st.progress(progress) 
                
                exterminator_name = st.text_input("Name of the Exterminator")
                if exterminator_name:
                    st.session_state.rent_own_info['exterminator_name'] = exterminator_name
                    progress += increment; bar14.progress(progress)     

                exterminator_number = st.text_input("Number for the Exterminator")
                if exterminator_number:
                    st.session_state.rent_own_info['exterminator_name'] = exterminator_number
                    progress += increment; bar14.progress(progress)   
            
                exterminator_description = st.text_area("When to contact the Exterminator?", placeholder="E.g. Heater not working, A/C not working, Electrical outlets stopped working, etc...")
                if exterminator_description: progress += increment; bar14.progress(progress)

            if 'Plumber' in homeowner_contacts_options:
                st.write("Plumber")
                progress = 0
                increment = 33
                bar15 = st.progress(progress) 
                
                plumber_name = st.text_input("Name of the Plumber")
                if plumber_name:
                    st.session_state.rent_own_info['plumber_name'] = plumber_name
                    progress += increment; bar15.progress(progress)     

                plumber_number = st.text_input("Number for the Plumber")
                if plumber_number:
                    st.session_state.rent_own_info['plumber_name'] = plumber_number
                    progress += increment; bar15.progress(progress)   
            
                plumber_description = st.text_area("When to contact the Plumber?", placeholder="E.g. Toilet clogged, drain clogged, garbage disposal stopped working, etc...")
                if plumber_description: progress += increment; bar15.progress(progress)

            if 'HOA' in homeowner_contacts_options:
                st.write("HOA")
                progress = 0
                increment = 25
                bar16 = st.progress(progress)
                
                property_management_name = st.text_input("Name of the Property Management Company")
                if property_management_name:
                    st.session_state.rent_own_info['property_management_name'] = property_management_name
                    progress += increment; bar16.progress(progress)     

                property_management_number = st.text_input("Number for the Property Management Company")
                if property_management_number:
                    st.session_state.rent_own_info['property_management_number'] = property_management_number
                    progress += increment; bar16.progress(progress)   

                property_management_email = st.text_input("Email for the Property Management Company")
                if property_management_email:
                    st.session_state.rent_own_info['property_management_email'] = property_management_email
                    progress += increment; bar16.progress(progress) 

                property_management_description = st.text_area("When to Contact Property Management Company", placeholder="E.g. Roof issues, leaking pipe, common areas issues, parking challenges, etc..")
                if property_management_description:
                    st.session_state.rent_own_info['property_management_description'] = property_management_description
                    progress += increment; bar16.progress(progress)

if __name__ == "__main__":
    main()


