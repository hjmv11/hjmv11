import os
import re

def rename_files_with_swapped_parts(folder_path):
    # Compile a regex pattern to match filenames with exactly one underscore
    pattern = re.compile(r'^([^_]+)_([^_]+)(\.[^.]+)$')
    
    # Iterate through all files in the specified folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # Skip directories
        if os.path.isdir(file_path):
            continue
            
        match = pattern.match(filename)
        if match:
            # Extract the parts of the filename
            first_part = match.group(1)
            second_part = match.group(2)
            extension = match.group(3)
            
            # Create the new filename by swapping the parts
            new_filename = f"{second_part}_{first_part}{extension}"
            
            # Get full paths for both old and new filenames
            new_path = os.path.join(folder_path, new_filename)
            
            # Rename the file
            try:
                os.rename(file_path, new_path)
                print(f"Renamed: {filename} -> {new_filename}")
            except OSError as e:
                print(f"Error renaming {filename}: {e}")

def process_folder_recursively(base_folder):
    # Walk through all directories and subdirectories
    for root, dirs, files in os.walk(base_folder):
        print(f"\nProcessing folder: {root}")
        rename_files_with_swapped_parts(root)

if __name__ == "__main__":
    base_folder = r"G:\My Drive\Personal\Language\Learn Japanese - Ultimate Getting Started with Japanese"
    
    if os.path.isdir(base_folder):
        print(f"Starting file renaming in: {base_folder}")
        process_folder_recursively(base_folder)
        print("\nFile renaming complete!")
    else:
        print("Invalid base folder path. Please verify the path exists.")