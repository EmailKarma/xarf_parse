import os
import json
import base64
from datetime import datetime
import glob

def decrypt_and_save(data, input_file_path, output_directory):
    # Check for the 'Report' key in the data
    if 'Report' in data:
        report_data = data['Report']
        # Check for the 'SmtpMailFromAddress' key in the 'Report' data
        smtp_mail_from_address = report_data.get('SmtpMailFromAddress', None)
    else:
        print(f"Error: 'Report' key not found in JSON. Skipping file: {input_file_path}")
        return

    # Check for the 'Sample' key and 'Payload' key within it
    if 'Sample' in data and isinstance(data['Sample'], dict) and 'Payload' in data['Sample']:
        encrypted_data = data['Sample']['Payload']
    elif 'Report' in data and 'Sample' in data['Report'] and 'Payload' in data['Report']['Sample']:
        encrypted_data = data['Report']['Sample']['Payload']
    else:
        print(f"Error: 'Payload' key not found in JSON. Skipping file: {input_file_path}")
        return

    # Decode base64
    decoded_data = base64.b64decode(encrypted_data).decode('utf-8', errors='replace')

    # Replace \r\n with actual newline character
    decoded_data = decoded_data.replace('\\r\\n', '\n')

    # Generate output file name with current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    base_filename = os.path.basename(input_file_path)

    output_filename = f'{current_date}_{base_filename}.txt'
    output_file_path = os.path.join(output_directory, output_filename)

    # Create the 'decrypted' directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Replace 'Payload' with the decrypted content
    data_copy = data.copy()
    if 'Sample' in data_copy and 'Payload' in data_copy['Sample']:
        data_copy['Sample']['Payload'] = decoded_data
    elif 'Report' in data_copy and 'Sample' in data_copy['Report'] and 'Payload' in data_copy['Report']['Sample']:
        data_copy['Report']['Sample']['Payload'] = decoded_data

    # Write the decrypted payload and original content to the new text file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(json.dumps(data_copy, indent=2))  # Write the decrypted payload and original content

    # Append value from '"SmtpMailFromAddress":' to the audit log file
    audit_log_path = os.path.join(output_directory, 'audit_log.txt')
    with open(audit_log_path, 'a', encoding='utf-8') as audit_log:
        audit_log.write(f"{current_date} - {base_filename}: 'SmtpMailFromAddress': {smtp_mail_from_address}\n")

    print(f"Decrypted payload and original content saved to {output_file_path}")

def decrypt_all_json_files(directory_path):
    input_file_paths = glob.glob(os.path.join(directory_path, '*.json'))
    output_directory = os.path.join(directory_path, 'decrypted')

    # Create or open the audit log file in append mode
    audit_log_path = os.path.join(output_directory, 'audit_log.txt')
    with open(audit_log_path, 'a', encoding='utf-8') as audit_log:
        pass  # Simply open the file to ensure it exists

    for file_path in input_file_paths:
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                decrypt_and_save(data, file_path, output_directory)

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in {file_path}: {e}")
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")

# Example usage with directory path
input_directory_path = r'C:\temp\xarf\files'
decrypt_all_json_files(input_directory_path)
