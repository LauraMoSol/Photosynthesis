# Import required modules
import time  # For timing execution
import os  # For file system operations
import re  # For regular expressions
import platform  # To detect operating system
from pathlib import Path  # For path handling
from tkinter import Tk, filedialog, messagebox  # For GUI interactions
from tqdm import tqdm  # For progress bar

# --- Prompt user to choose a folder ---
def choose_folder():
    root = Tk()
    root.withdraw()  # Hide the main window
    folder_selected = filedialog.askdirectory(title="Select Folder Containing JPK Files")  # Folder picker
    return Path(folder_selected) if folder_selected else None

# --- Ask user whether to save CSV in the same folder or not ---
def choose_save_location(default_folder):
    root = Tk()
    root.withdraw()
    answer = messagebox.askyesno("Save CSV", "Do you want to save the CSV in the same folder?")
    if answer:
        return default_folder  # Save in same folder
    else:
        other_folder = filedialog.askdirectory(title="Select Folder to Save CSV")  # Choose a different folder
        return Path(other_folder) if other_folder else None  # Return path or None if canceled

# --- Automatically open CSV with the default app ---
def open_csv(csv_path):
    system = platform.system()  # Get OS name
    if system == "Darwin":  # macOS
        os.system(f"open '{csv_path}'")
    elif system == "Windows":  # Windows
        os.startfile(csv_path)
    elif system == "Linux":  # Linux
        os.system(f"xdg-open '{csv_path}'")
    else:
        print("Unsupported OS. Please open the file manually.")

# --- Main ---
start_time = time.time()  # Start timing

# Ask user to choose the source folder
folder_path = choose_folder()
if not folder_path:
    print("No folder selected. Exiting.")
    exit()

# Ask where to save the CSV file
save_folder = choose_save_location(folder_path)
if not save_folder:
    print("No save location selected. Exiting.")
    exit()

# Parameters to search for in the files
parameters_to_find = [
    "relative-setpoint",
    "cantilever-calibration-info.calibration-environment",
    "cantilever-calibration-info.cantilever-name",
    "cantilever-calibration-info.defined",
    "cantilever-calibration-info.frequency",
    "cantilever-calibration-info.qFactor",
    "cantilever-calibration-info.sensitivity",
    "cantilever-calibration-info.spring-constant",
    "experiment-mode.name",
    "feedback-mode.adjust-reference-amplitude-feedback-settings.reference-amplitude",
]

# Create full path to the CSV file
csv_path = save_folder / "Parameters.csv"

# Open CSV file and write header
with open(csv_path, "w") as csv_file:
    csv_file.write("Filename," + ",".join(parameters_to_find) + "\n")

    # Collect all files (recursively) in the source folder
    files = list(folder_path.glob("**/*"))

    # Loop over each file
    for file_path in tqdm(files):
        if not file_path.is_file():
            continue  # Skip directories

        with open(file_path, "rb") as infile:
            data = infile.read()  # Read binary data

        text = data.decode("ISO-8859-1", errors="ignore")  # Decode to text
        row = {"Filename": file_path.name}  # Initialize row with filename

        # Search each parameter
        for parameter in parameters_to_find:
            pattern = rf"({re.escape(parameter)}) ?: ?(.*)"
            for line in text.splitlines():
                match = re.search(pattern, line)
                if match:
                    row[parameter] = match.group(2).strip()
                    break  # Stop at first match

        # Write row to CSV in correct column order
        values = [row.get(param, "") for param in ["Filename"] + parameters_to_find]
        csv_file.write(",".join(values) + "\n")

# Notify user
print(f"CSV file saved as {csv_path}")

# Print execution time
end_time = time.time()
print(f"Time in seconds: {round(end_time - start_time)}")

# Open the CSV file in the default program
open_csv(csv_path)
