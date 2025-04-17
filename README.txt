# File Organizer

This is a Python script that monitors a specified directory (default is the `Downloads` folder) and automatically moves files to appropriate subfolders based on their type. The script can be customized to monitor different file types such as audio, video, images, documents, and installers.

## Features

- **Real-time monitoring** of a specified folder.
- **Automatic categorization** of files:
  - Audio files are moved to `Downloaded Audio`.
  - Video files are moved to `Downloaded Video`.
  - Image files are moved to `Downloaded Images`.
  - Document files (including `.epub`, `.html`, `.xslm`) are moved to `Downloaded Documents`.
  - Installer files (e.g., `.pkg`, `.exe`, `.zip`) are moved to `Installers`.
- **GUI interface** for starting/stopping monitoring and selecting a folder to monitor.
- **Logging** of actions for reference.

## Requirements

- Python 3.x
- `watchdog` library (for file system monitoring)
- `tkinter` library (for the GUI, typically pre-installed with Python)

You can install the required libraries using `pip`:
```bash
pip install watchdog