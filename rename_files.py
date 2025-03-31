import os
import re

def rename_files_with_swapped_parts(folder_path):
    # Compile a regex pattern to match filenames with exactly one underscore
    pattern = re.compile(r'^([^_]+)_([^_]+)(\.[^.]+)$')
    
    # Iterate through all files in the specified folder
    for filename in os.listdir(folder_path):
        match = pattern.match(filename)
        if match:
            # Extract the parts of the filename
            first_part = match.group(1)
            second_part = match.group(2)
            extension = match.group(3)
            
            # Create the new filename by swapping the parts
            new_filename = f"{second_part}_{first_part}{extension}"
            
            # Get full paths for both old and new filenames
            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_filename)
            
            # Rename the file
            try:
                os.rename(old_path, new_path)
                print(f"Renamed: {filename} -> {new_filename}")
            except OSError as e:
                print(f"Error renaming {filename}: {e}")

if __name__ == "__main__":
    folder_path = input("Enter the folder path: ")
    if os.path.isdir(folder_path):
        rename_files_with_swapped_parts(folder_path)
        print("File renaming complete!")
    else:
        print("Invalid folder path. Please provide a valid directory.")