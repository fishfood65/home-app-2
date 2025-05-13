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
st.subheader("Level 1: Trainee")

st.write("Let's gather some information. Please enter your details:")

# Get user Input to enter input
city = st.text_input("Enter Your City:")
zip_code = st.text_input("Enter Your Zip Code:")
internet_provider = st.text_input("Enter Your Internet Provider Name:")

# Save the user input for later use
user_info = {"city": city, "zip_code": zip_code, "internet_provider":internet_provider}

# Display a button and perform an action based on user input
if st.button("Click to Accept Level 1: Trainee Mission"):
    st.write(f"You entered: {city}, {zip_code}, {internet_provider}. We'll provide personalized utilities informaion for your area.")

# Read user_info to get city and zip_code
city = user_info["city"]
zip_code = user_info["zip_code"]
internet_provider = user_info["internet_provider"]

def start_timer():
    st.session_state.started = True
    while st.session_state.started and st.session_state.time_left > 0:
        st.session_state.time_left -= 1
        st.write(f"Time left: {st.session_state.time_left} seconds")
        time.sleep(1)
        st.experimental_rerun()
    st.write("Timer is up!")
    st.markdown(
        '<i class="fas fa-bell"></i>',
        unsafe_allow_html=True,
        help='<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css">'
    )

if "started" not in st.session_state:
    st.session_state.started = False

if "time_left" not in st.session_state:
    st.session_state.time_left = 60

if not st.session_state.started:
    if st.button("Start Timer"):
        start_timer()
else:
    st.write("Timer is running...")

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

st.subheader("Level 2: Mail Handling and Trash Disposal")

# Main entry point of the app
def main():
    # Call the trash_handling function
    mail()
    trash_handling()

def mail():
    st.write("Mail Handling Instructions")

    # Initialize user_info in session state
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {}

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

        # Save user input into user_info
        if st.button("Mail Handling 100% Complete. Click to Save"):
            st.session_state.user_info = {
                "Mailbox Location": mailbox_location,
                "Mailbox Key": mailbox_key,
                "Pick-Up Schedule": pick_up_schedule,
                "What to Do with the Mail": what_to_do_with_mail,
                "Packages": What_to_do_with_packages
            }
            st.success("User information saved successfully!")

    # Display the saved user information
    st.write("Saved Mail Handing Information")
    if st.session_state.user_info:
        with st.expander("Saved User Information", expanded=True):
            for key, value in st.session_state.user_info.items():
                st.write(f"{key}: {value}")
    else:
        st.write("No user information saved yet.")

def trash_handling():
    st.markdown("Trash Disposal Instructions")

    # Initialize session state
    if 'trash_info' not in st.session_state:
        st.session_state.trash_info = {}
    if 'trash_images' not in st.session_state:
        st.session_state.trash_images = {}

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    times = ["Morning", "Afternoon", "Evening"]

    with st.expander("Kitchen and Bath Trash Details", expanded=True):
        # Indoor Trash Info
        st.markdown("##### Fill in the kitchen and bathroom trash info")

        progress = 0
        increment = 20
        bar1 = st.progress(progress)

        kitchen_bin_location = st.text_area(
            "Kitchen Trash Bin Location", 
            key="kitchen_bin_location",
            placeholder="Describe where the kitchen trash bin is located. For example, 'Under the kitchen sink' or 'Next to the fridge.'"
            )
        if kitchen_bin_location:
            progress += increment
            bar1.progress(progress)
        
        bathroom_bin_location = st.text_area(
            "Bathroom Trash Bin Location", 
            key="bathroom_bin_location",
            placeholder="Describe where the bathroom trash bin is located. For example, 'Near the toilet' or 'Under the bathroom counter.'"
            )
        if bathroom_bin_location:
            progress += increment
            bar1.progress(progress)

        trash_bag_type = st.text_area(
            "Trash Bag Type & Location", 
            key="trash_bag_type",
            placeholder="Please describe the type of trash bags used and where they are stored. For example, 'Black trash bags stored in the pantry.'"
            )
        if trash_bag_type:
            progress += increment
            bar1.progress(progress)

        emptying_schedule = st.text_area(
            "Emptying Schedule", 
            key="emptying_schedule",
            placeholder="Indicate how often the trash should be emptied. For example, 'Empty every night' or 'Once a week on Tuesdays.'"
            )
        if emptying_schedule:
            progress += increment
            bar1.progress(progress)

        replacement_instructions = st.text_area(
            "Replacing Trash Bags", 
            key="replacement_instructions",
            placeholder="Instructions for replacing trash bags. For example, 'Replace bag when full and tie the bag securely.'"
            )
        if replacement_instructions:
            progress += increment
            bar1.progress(progress)

        # Outdoor bin info
    with st.expander("Outdoor Bin Details", expanded=True):
        st.markdown("##### Outdoor Bin Handling Details")

        progress = 0
        increment = 33
        bar2 = st.progress(progress)
       
        bin_destination = st.text_area(
            "Where to Empty the Trash Bins", 
            key="bin_destination",
            placeholder="Describe where to empty the outdoor trash bins. For example, 'By the curb on pickup day' or 'Behind the garage.'"
            )
        
        if bin_destination:
            progress += increment
            bar2.progress(progress)

        bin_description = st.text_area(
            "What the Outdoor Trash Bins Look Like", 
            key="bin_description",
            placeholder="Describe the appearance of the outdoor trash bins. For example, 'Green with a lid, marked with a recycling symbol.'"
            )
        
        if bin_description:
            progress += increment
            bar2.progress(progress)

        bin_location_specifics = st.text_area(
            "Specific Location or Instructions for Outdoor Bins", 
            key="bin_location_specifics",
            placeholder="Provide any additional details or specific locations for the outdoor bins. For example, 'Next to the side gate.'"
            )
        
        if bin_location_specifics:
            progress += increment
            bar2.progress(progress)

        # Handle image upload or display for outdoor bin
        def handle_image(label, display_name):
            uploaded = None
            image_key = f"{label} Image"
            if label not in st.session_state.trash_images:
                st.session_state.trash_images[label] = None

            if st.session_state.trash_images[label]:
                st.image(Image.open(io.BytesIO(st.session_state.trash_images[label])), caption=display_name)
                if st.button(f"Delete {display_name}", key=f"delete_{label}"):
                    st.session_state.trash_images[label] = None
                    st.experimental_rerun()
            else:
                uploaded = st.file_uploader(
                    f"Upload a photo of the {display_name}", 
                    type=["jpg", "jpeg", "png"], 
                    key=f"{label}_upload",
                    help="Upload a clear imapge of the specified trash bin or area")
                if uploaded:
                    st.session_state.trash_images[label] = uploaded.read()
                    st.success(f"{display_name} image uploaded.")
                    st.experimental_rerun()

        handle_image("Outdoor Bin", "Outdoor Trash Bin")
        handle_image("Recycling Bin", "Recycling Bin")

        # Collection schedule
        st.markdown("##### Collection Schedule")
        trash_day = st.selectbox(
            "Garbage Pickup Day", 
            days, 
            key="trash_day",
            help="Select the day of the week for garbage pickup."
            )
        trash_time = st.selectbox(
            "Garbage Pickup Time", 
            times, 
            key="trash_time",
            help="Select the day of the week for garbage pickup." 
            )
        recycling_day = st.selectbox(
            "Recycling Pickup Day", 
            days, 
            key="recycling_day",
            help="Select the time of day for garbage pickup (Morning, Afternoon, or Evening)."
            )
        recycling_time = st.selectbox(
            "Recycling Pickup Time", 
            times, 
            key="recycling_time",
            help="Select the day of the week for recycling pickup."
            )

        bin_handling_instructions = st.text_area("Instructions for Placing and Returning Outdoor Bins", key="bin_handling_instructions")

        # Common disposal area
        st.markdown("##### Common Disposal Area")
        uses_common_disposal = st.checkbox(
            "Is there a common disposal area?", 
            key="uses_common_disposal",
            help= "Check this box if there is a common disposal area where trash and recycling should be placed."
            )
        common_area_instructions = ""
        if uses_common_disposal:
            common_area_instructions = st.text_area(
                "Instructions for Common Disposal Area", 
                key="common_area_instructions",
                placeholder= "Describe how to use the common disposal area. For example, 'Place trash bags in the designated dumpster in the alley.'"
                )
            handle_image("Common Area", "Common Disposal Area")

        # Compost
        compost_applicable = st.checkbox(
            "Is composting used?", 
            key="compost_applicable",
            help="Check this box if composting is used at this location."
            )
        compost_instructions = ""
        if compost_applicable:
            compost_instructions = st.text_area(
                "Compost Instructions", 
                key="compost_instructions",
                placeholder="Describe how to handle compost. For example, 'Place all organic waste in the compost bin on the left side of the yard.'"
                )

        # Waste Management Contact Info
        st.markdown("##### Waste Management Company Contact Information")
        wm_name = st.text_input(
            "Waste Management Contact Company", 
            key="wm_name",
            placeholder="Enter the name of waste management company"
            )
        wm_phone = st.text_input(
            "Waste Management Contact Phone", 
            key="wm_phone",
            placeholder="Enter the contact phone number for waste management."
            )
        wm_description = st.text_area(
            "When to call Waste Management Company", 
            key="wm_description",
            placeholder= "Provide brief instrucitons for contacting the waste management company (e.g., 'For billing inquiries' or 'To report missed pickup') and information needed to provide the company when contacting them." 
            )

        # Save
        if st.button("Trash Handling 100% Complete. Click to Save"):
            # Save text data
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

            # Save images in session state
            st.session_state.trash_images = {}  # Reset

            def store_image(file, label):
                if file is not None:
                    image_bytes = file.read()
                    st.session_state.trash_images[label] = image_bytes
                    st.success(f"{label} image saved.")
                else:
                    st.session_state.trash_images[label] = None

            store_image(outdoor_bin_photo, "Outdoor Bin Photo")
            store_image(recycling_bin_photo, "Recycling Bin Photo")
            if uses_common_disposal:
                store_image(common_area_photo, "Common Disposal Area Photo")

            st.success("All trash handling instructions and images saved successfully!")

    # Display saved info and images
    st.markdown("##### Saved Trash Handling Information")
    if st.session_state.trash_info:
        for key, value in st.session_state.trash_info.items():
            st.write(f"**{key}**: {value}")

    st.markdown("##### Uploaded Photos")
    for label, image_bytes in st.session_state.trash_images.items():
        if image_bytes:
            st.image(Image.open(io.BytesIO(image_bytes)), caption=label)

# Run the app if this script is executed
if __name__ == "__main__":
    main()
