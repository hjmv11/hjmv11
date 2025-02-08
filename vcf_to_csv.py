import csv
import re
from vobject import readComponents

# Define updated headers for the CSV file
headers = [
    "Name Prefix", "First Name", "Middle Name", "Last Name", "Name Suffix",
    "Phonetic First Name", "Phonetic Middle Name", "Phonetic Last Name", "Nickname",
    "File As", "E-mail 1 - Label", "E-mail 1 - Value", "E-mail 2 - Label", "E-mail 2 - Value",
    "Phone 1 - Label", "Phone 1 - Value", "Phone 2 - Label", "Phone 2 - Value",
    "Address 1 - Label", "Address 1 - Country", "Address 1 - Street", "Address 1 - Extended Address",
    "Address 1 - City", "Address 1 - Region", "Address 1 - Postal Code", "Address 1 - PO Box",
    "Address 2 - Label", "Address 2 - Country", "Address 2 - Street", "Address 2 - Extended Address",
    "Address 2 - City", "Address 2 - Region", "Address 2 - Postal Code", "Address 2 - PO Box",
    "Organization Name", "Organization Title", "Organization Department", "Birthday",
    "Event 1 - Label", "Event 1 - Value", "Relation 1 - Label", "Relation 1 - Value",
    "Website 1 - Label", "Website 1 - Value", "Custom Field 1 - Label", "Custom Field 1 - Value", "Notes", "Labels"
]

# Function to clean and format phone numbers
def format_phone_number(phone):
    if not phone:
        return ""
    # Special case for +50235712230
    if phone == "+50235712230":
        return "+502 3571-2230"
    # Remove all non-numeric characters
    cleaned = re.sub(r"[^0-9]", "", phone)
    if len(cleaned) == 10:
        return f"+1 {cleaned[:3]}-{cleaned[3:6]}-{cleaned[6:]}"
    elif len(cleaned) > 10:
        return f"+{cleaned[:-10]} {cleaned[-10:-7]}-{cleaned[-7:-4]}-{cleaned[-4:]}"
    elif len(cleaned) < 10:
        return f"{cleaned}"
    return phone  # Return original if formatting fails

# Function to standardize labels
def standardize_label(label, label_type):
    label = label.upper()  # Make case-insensitive
    if label_type == "email":
        if label in ["HOME", "OTHER", "WORK"]:
            return label
        return "HOME"  # Default to WORK for emails
    elif label_type == "phone":
        if label in ["HOME", "MOBILE", "WORK"]:
            return label
        return "MOBILE"  # Default to MOBILE for phones
    return label

# Function to extract data from a VCF contact
def extract_contact_data(contact):
    data = {header: "" for header in headers}  # Initialize all fields as empty

    # Extract name
    if hasattr(contact, "n"):
        name_parts = contact.n.value
        data["First Name"] = name_parts.given or ""
        data["Last Name"] = name_parts.family or ""
        data["Middle Name"] = name_parts.additional or ""

    # Extract organization
    if hasattr(contact, "org"):
        data["Organization Name"] = contact.org.value[0] if contact.org.value else ""

    # Extract birthday
    if hasattr(contact, "bday"):
        birthday = contact.bday.value
        # Clean birthday (remove non-numeric characters)
        data["Birthday"] = re.sub(r"[^0-9]", "", birthday)

    # Extract notes
    if hasattr(contact, "note"):
        notes = contact.note.value
        # Check notes for Other: or Work: and clean up
        if re.search(r"Other: ", notes) or re.search(r"Work: ", notes):
            notes = re.sub(r"Other: ", "", notes)
            notes = re.sub(r"Work: ", "", notes)
            notes = re.sub(r"[ \-]", "", notes)
        # Check for phone numbers in notes if Phone 1 and Phone 2 are empty
        if not data["Phone 1 - Value"] and not data["Phone 2 - Value"]:
            # Extract phone numbers with or without country code having 5 or more digits
            phone_numbers = re.findall(r"\+?\d{5,}", notes)
            if phone_numbers:
                if len(phone_numbers[0]) < 12:
                    data["Phone 1 - Label"] = "WORK"
                else:
                    data["Phone 1 - Label"] = "MOBILE"
                data["Phone 1 - Value"] = format_phone_number(phone_numbers[0])
            notes = re.sub(r"\+?\d{5,}", "", notes)  # Remove phone numbers from notes
        #Check for phone numbers in notes if Phone 1 is not empty and Phone 2 is empty
        elif data["Phone 1 - Value"] and not data["Phone 2 - Value"]:
            # Extract phone numbers with or without country code having 5 or more digits
            phone_numbers = re.findall(r"\+?\d{5,}", notes)
            if phone_numbers and phone_numbers[0] != data["Phone 1 - Value"]: # Check if phone number is different
                data["Phone 2 - Label"] = "OTHER"
                data["Phone 2 - Value"] = format_phone_number(phone_numbers[0])
            notes = re.sub(r"\+?\d{5,}", "", notes)  # Remove phone numbers from notes
        # Check notes for Code, Pin, or Enter if not empty
        if not re.search(r"CODE|PIN|ENTER", notes.capitalize()):
            if re.search(r":", notes):
                notes = ""  # Clear notes if no relevant information found
        data["Notes"] = notes

    # Extract emails
    emails = contact.contents.get("email", [])
    for i, email in enumerate(emails[:2]):  # Limit to 2 emails
        label = email.params.get("TYPE", ["HOME"])[0]
        label = standardize_label(label, "email")  # Standardize email label
        value = email.value
        data[f"E-mail {i+1} - Label"] = label
        data[f"E-mail {i+1} - Value"] = value

    # Extract phones
    phones = contact.contents.get("tel", [])
    phone_labels = []
    for i, phone in enumerate(phones[:2]):  # Limit to 2 phones
        label = phone.params.get("TYPE", ["MOBILE"])[0]
        label = standardize_label(label, "phone")  # Standardize phone label
        phone_labels.append(label)
        value = format_phone_number(phone.value)
        data[f"Phone {i+1} - Label"] = label
        data[f"Phone {i+1} - Value"] = value

    # Handle multiple phone labels
    if len(phone_labels) == 2:
        if "WORK" not in phone_labels:
            data["Phone 2 - Label"] = "OTHER"

    # Extract addresses
    addresses = contact.contents.get("adr", [])
    for i, address in enumerate(addresses[:2]):  # Limit to 2 addresses
        label = address.params.get("TYPE", ["Address"])[0]
        street = address.value.street or ""
        city = address.value.city or ""
        region = address.value.region or ""
        postal_code = address.value.code or ""
        country = address.value.country or ""
        # Handle PO Box (if present in the street field)
        pobox = ""
        if "PO Box" in street:
            pobox = street.split("PO Box")[1].strip()
            street = street.split("PO Box")[0].strip()
        data[f"Address {i+1} - Label"] = label
        data[f"Address {i+1} - Street"] = street
        data[f"Address {i+1} - City"] = city
        data[f"Address {i+1} - PO Box"] = pobox
        data[f"Address {i+1} - Region"] = region
        data[f"Address {i+1} - Postal Code"] = postal_code
        data[f"Address {i+1} - Country"] = country

    return data

# Read VCF file and write to CSV
def vcf_to_csv(vcf_file_path, csv_file_path):
    with open(vcf_file_path, "r", encoding="utf-8") as vcf_file:
        vcf_data = vcf_file.read()

    contacts = []
    for contact in readComponents(vcf_data):  # Use readComponents to parse all vCards
        contacts.append(extract_contact_data(contact))

    # Write to CSV
    with open(csv_file_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(contacts)

# Run the script
if __name__ == "__main__":
    vcf_file_path = "G:\\My Drive\\Personal\\Contact List\\iCloudExport.vcf"  # Updated path to your VCF file
    csv_file_path = "G:\\My Drive\\Personal\\Contact List\\GoogleImport.csv"  # Path to save the CSV file
    vcf_to_csv(vcf_file_path, csv_file_path)
    print(f"Conversion complete. CSV saved to {csv_file_path}")