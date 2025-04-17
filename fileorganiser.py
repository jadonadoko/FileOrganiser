import os
import logging
import webbrowser
from os import scandir, rename
from os.path import splitext, exists, join
from shutil import move
from time import sleep
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
from tkinter import ttk, filedialog

# Default source and destination folders
source_dir = os.path.expanduser("~/Downloads")  # The folder to monitor
dest_dir_audio = os.path.join(source_dir, "Downloaded Audio")
dest_dir_video = os.path.join(source_dir, "Downloaded Video")
dest_dir_image = os.path.join(source_dir, "Downloaded Images")
dest_dir_documents = os.path.join(source_dir, "Downloaded Documents")
dest_dir_installers = os.path.join(source_dir, "Installers")

# Ensure destination folders exist
for folder in [dest_dir_audio, dest_dir_video, dest_dir_image, dest_dir_documents, dest_dir_installers]:
    os.makedirs(folder, exist_ok=True)  # Create destination folders if they don't exist
    print(f"Ensured directory exists: {folder}")

# File extensions for different categories
image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg", ".ico"]
video_extensions = [".mp4", ".mkv", ".avi", ".mov", ".flv", ".webm"]
audio_extensions = [".m4a", ".flac", ".mp3", ".wav", ".aac", ".wma"]
document_extensions = [".doc", ".docx", ".pdf", ".xls", ".xlsx", ".ppt", ".pptx", ".epub", ".xslm", ".html"]
installer_extensions = [".exe", ".dmg", ".pkg", ".zip"]

file_counts = {"audio": 0, "video": 0, "image": 0, "document": 0, "installer": 0}

# Function to create unique filenames if a file already exists in the destination
def make_unique(dest, name):
    filename, extension = splitext(name)
    counter = 1
    while exists(f"{dest}/{name}"):
        name = f"{filename}({str(counter)}){extension}"
        counter += 1
    return name

# Function to move files to the appropriate destination folder
def move_file(dest, entry, name):
    print(f"Checking if {name} needs to be renamed to avoid conflict in {dest}...")
    final_name = name
    if exists(f"{dest}/{name}"):
        unique_name = make_unique(dest, name)
        oldName = join(dest, name)
        newName = join(dest, unique_name)
        print(f"Renaming {oldName} to {newName}")
        rename(oldName, newName)
        final_name = unique_name
    print(f"Moving {entry.path} to {dest}")
    move(entry.path, join(dest, final_name))
    log_and_display(f"Moved file: {final_name} to {dest}", file_path=join(dest, final_name))

# Function to log and display actions
def log_and_display(message, file_path=None):
    print(message)
    logging.info(message)
    if log_display:
        if file_path:
            log_display.insert(tk.END, message + "\n", ("link", file_path))
            log_display.insert(tk.END, "\n\n")
        else:
            log_display.insert(tk.END, message + "\n\n")
        log_display.yview(tk.END)

# File system event handler to detect file changes
class FileMover(FileSystemEventHandler):
    def on_modified(self, event):
        print(f"Modification detected in {source_dir}")
        with scandir(source_dir) as entries:
            for entry in entries:
                if entry.is_file():
                    name = entry.name
                    print(f"Checking file: {name}")
                    self.check_audio_files(entry, name)
                    self.check_video_files(entry, name)
                    self.check_image_files(entry, name)
                    self.check_document_files(entry, name)
                    self.check_installer_files(entry, name)
        log_and_display(f"Current count - Audio: {file_counts['audio']}, Video: {file_counts['video']}, Image: {file_counts['image']}, Document: {file_counts['document']}, Installer: {file_counts['installer']}")

    # Check if the file is an audio file
    def check_audio_files(self, entry, name):
        for ext in audio_extensions:
            if name.lower().endswith(ext):
                print(f"Audio file detected: {name} -> {dest_dir_audio}")
                move_file(dest_dir_audio, entry, name)
                file_counts["audio"] += 1
                break

    # Check if the file is a video file
    def check_video_files(self, entry, name):
        for ext in video_extensions:
            if name.lower().endswith(ext):
                print(f"Video file detected: {name} -> {dest_dir_video}")
                move_file(dest_dir_video, entry, name)
                file_counts["video"] += 1
                break

    # Check if the file is an image file
    def check_image_files(self, entry, name):
        for ext in image_extensions:
            if name.lower().endswith(ext):
                print(f"Image file detected: {name} -> {dest_dir_image}")
                move_file(dest_dir_image, entry, name)
                file_counts["image"] += 1
                break

    # Check if the file is a document file
    def check_document_files(self, entry, name):
        for ext in document_extensions:
            if name.lower().endswith(ext):
                print(f"Document file detected: {name} -> {dest_dir_documents}")
                move_file(dest_dir_documents, entry, name)
                file_counts["document"] += 1
                break

    # Check if the file is an installer file
    def check_installer_files(self, entry, name):
        for ext in installer_extensions:
            if name.lower().endswith(ext):
                print(f"Installer file detected: {name} -> {dest_dir_installers}")
                move_file(dest_dir_installers, entry, name)
                file_counts["installer"] += 1
                break

# Logging setup
logging.basicConfig(
    filename="file_organizer.log",
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# GUI setup
def start_gui():
    global log_display, observer, observer_running, source_dir

    # Function to toggle observer (start/stop monitoring)
    def toggle_observer():
        nonlocal observer_button
        if observer_running[0]:
            stop_observer()
            observer_button.config(text="Start Monitoring")
            log_and_display("Monitoring stopped.")
        else:
            start_observer()
            observer_button.config(text="Stop Monitoring")
            log_and_display(f"Monitoring started for folder: {source_dir}")

    # Function to select a new folder to monitor
    def select_folder():
        global source_dir
        selected = filedialog.askdirectory()
        if selected:
            stop_observer()  # Stop the observer before changing the folder
            print(f"New folder selected: {selected}")
            source_dir = selected
            folder_label.config(text=f"Monitoring: {source_dir}")
            log_and_display(f"Folder selected: {source_dir}")

    # GUI window
    root = tk.Tk()
    root.title("File Organizer")
    root.geometry("700x550")
    root.configure(bg="#f5f5f5")

    title = ttk.Label(root, text="File Organizer", font=("Segoe UI", 16, "bold"))
    title.pack(pady=10)

    # Start/Stop button
    observer_button = ttk.Button(root, text="Start Monitoring", command=toggle_observer)
    observer_button.pack(pady=5)

    # Folder selection button
    folder_button = ttk.Button(root, text="Select Folder to Monitor", command=select_folder)
    folder_button.pack(pady=5)

    folder_label = ttk.Label(root, text=f"Monitoring: {source_dir}", wraplength=600)
    folder_label.pack(pady=5)

    # Log display area
    log_display = tk.Text(root, wrap=tk.WORD, height=25, width=85, bg="white", font=("Segoe UI", 10))
    log_display.pack(padx=10, pady=10)

    # Configure clickable link in log display
    log_display.tag_config("link", foreground="blue", underline=1)

    def on_click(event):
        index = log_display.index(f"@{event.x},{event.y}")
        tags = log_display.tag_names(index)
        for tag in tags:
            if os.path.exists(tag):
                folder = os.path.dirname(tag)
                print(f"Opening folder: {folder}")
                webbrowser.open(folder)

    log_display.tag_bind("link", "<Button-1>", on_click)

    root.mainloop()

# Observer setup
observer = Observer()
observer_running = [False]

# Start the file observer
def start_observer():
    global observer
    print(f"Starting observer for {source_dir}...")
    event_handler = FileMover()
    observer.schedule(event_handler, source_dir, recursive=True)
    observer.start()
    observer_running[0] = True

# Stop the file observer
def stop_observer():
    global observer
    if observer_running[0]:
        print("Stopping observer...")
        observer.stop()
        observer.join()

# Start the GUI
start_gui()
