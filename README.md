# Gmail-organizer

Gmail-organizer is a Python project designed to help you automate the organization of your Gmail inbox. With customizable rules and seamless integration with the Gmail API, this tool can label, sort, move, or delete emails based on your preferences—saving you time and keeping your inbox tidy.

## Features

- **Automatic labeling:** Apply labels to emails based on sender, subject, or keywords.
- **Inbox sorting:** Move emails to folders according to custom rules.
- **Bulk actions:** Process large volumes of emails efficiently.
- **Customizable rules:** Easily edit or add your own filter rules.
- **Secure authentication:** Uses OAuth 2.0 for secure access to your Gmail account.
- **Logging:** Keep track of actions taken for transparency and debugging.

## Requirements

- Python 3.7+
- Gmail account
- Google Cloud project with Gmail API enabled

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/anshu-18/Gmail-organizer.git
   cd Gmail-organizer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Gmail API credentials**
   - Go to [Google Cloud Console](https://console.developers.google.com/).
   - Create a new project and enable the Gmail API.
   - Create OAuth 2.0 credentials and download `credentials.json`.
   - Place `credentials.json` in the project root directory.

## Usage

1. **Configure your rules.**
   - ```bash
     uvicorn rule_endpoints:app --reload
     ```
   -  Run rule_endpoints.py to manage the label-keyword rule APIs to specify how emails should be organized.

2. **Run the organizer**
   ```bash
   python main.py
   ```

3. **Authorize the application.**
   - On the first run, your browser will open to request access to your Gmail account.

4. **Check results**
   - Emails will be labeled, moved, or processed according to your configuration.
   - Review the logs for details on actions performed.


*Keep your inbox organized and stress-free with Gmail-organizer!*
