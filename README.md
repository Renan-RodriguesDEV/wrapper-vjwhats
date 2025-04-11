# WhatsApp Library

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)

A Python library that provides a convenient interface to interact with WhatsApp Web using Selenium.
This library automates WhatsApp Web operations, enabling message sending, file sharing, and conversation management through Python code.

Developed by Renan, primarily used by VJ Bots for automation solutions.

## Features

- 🔍 Find and open conversations by username or phone number
- 💬 Send text messages programmatically
- 📎 Share files, images, and documents
- 📱 Start new conversations with unsaved contacts
- 🔄 Automated session handling with Chrome profiles

## Installation

Install the WhatsApp library and its dependencies:

```bash
# Install required dependencies
pip install selenium

# Clone the repository (or install via pip if published)
git clone https://github.com/username/vjwhats.git
cd vjwhats
pip install -e .
```

## Usage Example

```python
from vjwhats import WhatsApp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pathlib import Path

def main():
    # Set up Chrome with an existing user profile (to use saved WhatsApp Web session)
    chrome_options = Options()
    chrome_options.add_argument("user-data-dir=C:/Users/EXAMPLE/AppData/Local/Google/Chrome/User Data")
    chrome_options.add_argument("profile-directory=Default")

    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    # Create WhatsApp instance
    wpp = WhatsApp(driver)

    # Example 1: Send message to existing contact
    wpp.find_by_username("Contact 1")
    wpp.send_message("Hello, this is a test message!")

    # Example 2: Send file to another contact
    wpp.find_by_username("Contact 2")
    wpp.send_file(Path("path/to/file"), which=1)  # 'which=1' refers to file selector type

    # Example 3: Start conversation with new number and send a file
    wpp.start_conversation("+55999977885")  # Format with country code
    wpp.send_file(Path("path/to/file"), which=1)

    # Close driver when finished
    # driver.quit()

if __name__ == "__main__":
    main()
```

## API Reference

### Core Functions

- `__init__(driver)` - Initialize with Selenium WebDriver
- `find_by_username(username)` - Open chat with specific contact
- `send_message(message)` - Send text message to current chat
- `send_file(file_path, which=1)` - Send file to current chat
- `start_conversation(phone)` - Start new chat with phone number

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
