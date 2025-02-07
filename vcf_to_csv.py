import csv
from vobject import readComponents  # Use readComponents instead of readOne

# Define headers for the CSV file
headers = [
    "First Name", "Last Name", "Organization Name", "Birthday", "Notes",
    "E-mail 1 - Label", "E-mail 1 - Value", "E-mail 2 - Label", "E-mail 2 - Value",
    "Phone 1 - Label", "Phone 1 - Value", "Phone 2 - Label", "Phone 2 - Value",
    "Address 1 - Label", "Address 1 - Street", "Address 1 - City", "Address 1 - PO Box",
    "Address 1 - Region", "Address 1 - Postal Code", "Address 1 - Country",
    "Address 2 - Label", "Address 2 - Street", "Address 2 - City", "Address 2 - PO Box",
    "Address 2 - Region", "Address 2 - Postal Code", "Address 2 - Country"
]

# Function to extract data from a VCF contact
def extract_contact_data(contact):
    data = {header: "" for header in headers}  # Initialize all fields as empty

    # Extract name
    if hasattr(contact, "n"):
        name_parts = contact.n.value
        data["First Name"] = name_parts.given or ""
        data["Last Name"] = name_parts.family or ""

    # Extract organization
    if hasattr(contact, "org"):
        data["Organization Name"] = contact.org.value[0] if contact.org.value else ""

    # Extract birthday
    if hasattr(contact, "bday"):
        data["Birthday"] = contact.bday.value

    # Extract notes
    if hasattr(contact, "note"):
        data["Notes"] = contact.note.value

    # Extract emails
    emails = contact.contents.get("email", [])
    for i, email in enumerate(emails[:2]):  # Limit to 2 emails
        label = email.params.get("TYPE", ["E-mail"])[0]
        value = email.value
        data[f"E-mail {i+1} - Label"] = label
        data[f"E-mail {i+1} - Value"] = value

    # Extract phones
    phones = contact.contents.get("tel", [])
    for i, phone in enumerate(phones[:2]):  # Limit to 2 phones
        label = phone.params.get("TYPE", ["Phone"])[0]
        value = phone.value
        data[f"Phone {i+1} - Label"] = label
        data[f"Phone {i+1} - Value"] = value

    # Extract addresses
    addresses = contact.contents.get("adr", [])
    for i, address in enumerate(addresses[:2]):  # Limit to 2 addresses
        label = address.params.get("TYPE", ["Address"])[0]
        street = address.value.street or ""
        city = address.value.city or ""
        pobox = address.value.pobox or ""
        region = address.value.region or ""
        postal_code = address.value.code or ""
        country = address.value.country or ""
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
        print(contact)  # Debug: Print each contact
        contacts.append(extract_contact_data(contact))

    # Write to CSV
    with open(csv_file_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(contacts)

# Run the script
if __name__ == "__main__":
    vcf_file_path = "G:\\My Drive\\Personal\\Contact List\\iCloudContacts02052025.vcf"  # Updated path to your VCF file
    csv_file_path = "G:\\My Drive\\Personal\\Contact List\\contacts.csv"  # Path to save the CSV file
    vcf_to_csv(vcf_file_path, csv_file_path)
    print(f"Conversion complete. CSV saved to {csv_file_path}")