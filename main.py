import os.path
import json
import base64
import quopri

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from pymongo import MongoClient
from connection_string import MONGO_URI

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly",
          "https://www.googleapis.com/auth/gmail.labels", 
          "https://www.googleapis.com/auth/gmail.modify"]


'''''
def load_keywords(json_file):
  """Load keywords from a JSON file"""

  with open(json_file, "r") as file:
    return json.load(file)
'''
def load_rules_from_db():
  """Load rules from MongoDB"""
  client = MongoClient(MONGO_URI)
  db = client["GMAIL_RULES_DB"]
  collection = db["labels_keywords"]

  try:
    all_rules = list(collection.find())
    # Format the rules into the dictionary structure process_emails expects
    # e.g., {'Promotions': ['unsubscribe', 'sale'], 'Social': ['facebook']}
    keywords_dict = {}
    for rule in all_rules:
        if "label" in rule and "keywords" in rule:
            keywords_dict[rule["label"]] = rule["keywords"]
            
    print("Successfully loaded rules from database.")
    return keywords_dict
  except Exception as e:
    print(f"Error fetching rules from database: {e}")  

def create_label(service, label_name):
  """Create a label in Gmail"""

  #chk if label already exists
  results = service.users().labels().list(userId="me").execute()
  existing_labels = results.get("labels", [])
  for label in existing_labels:
    if label["name"].lower() == label_name.lower():
      print(f"Label '{label_name}' already exists.")
      return label["id"]

  label_body = {
    "name": label_name,
    "labelListVisibility": "labelShow",
    "messageListVisibility": "show"
  }
  try:
    label = service.users().labels().create(userId="me", body=label_body).execute()
    return label["id"]
  except HttpError as error:
    print(f"An error occurred while creating label: {error}")
    return None


def apply_label(service, msg_id, label_id):
  """Apply label to the email message"""

  try:
    service.users().messages().modify(
      userId="me",
      id=msg_id,
      body={"addLabelIds": [label_id],
            "removeLabelIds": ["INBOX"]},  # remove mail from inbox
    ).execute()
    print(f"Label applied to message ID: {msg_id}")

  except HttpError as error:
    print(f"An error occurred while applying label: {error}")


def process_emails(service, keywords):
  """Read emails, identify keywords and label them"""

  try:
    results = service.users().messages().list(userId="me").execute()
    msg = results.get("messages", [])
    next_page_token = results.get("nextPageToken")
    
    # Loop through all pages of messages
    while next_page_token:
      results = service.users().messages().list(userId="me", pageToken=next_page_token).execute()
      msg.extend(results.get("messages", []))
      next_page_token = results.get("nextPageToken")
      print(f"Next page token: {next_page_token}")
      
    #breakpoint()
    if not msg:
      print(f"No emails present")
      return
    else:
      print(f"Total emails: {len(msg)}")

    for i in msg:
      msg_id = i["id"]
      m1 = service.users().messages().get(userId="me",id=msg_id).execute()
      payload = m1.get("payload", {})
      headers = payload.get("headers", [])
      body = payload.get("body", {}).get("data", "")

      decoded_body = base64.urlsafe_b64decode(body).decode("utf-8", errors="ignore")
      #print(decoded_body)
      #breakpoint()
      decoded_body = quopri.decodestring(decoded_body.encode("utf-8", errors="ignore")).decode("utf-8", errors="ignore")

      for key, values in keywords.items():
        for val in values:
          if val.lower() in decoded_body.lower():
            print(f"keywords found in email : {val}, create label: {key}")
            # Create label
            label_id = create_label(service, key)
            if label_id:
              apply_label(service, i["id"], label_id)
            else:
              break
  except HttpError as error:
    print(f"An error occurred: {error}")


def main():
  """
    Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
  """
  
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "gmail-credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  """
  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    results = service.users().labels().list(userId="me").execute()
    labels = results.get("labels", [])

    if not labels:
      print("No labels found.")
      return
    print("Labels:")
    for label in labels:
      print(label["name"])

  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")
  """

  try:
    service = build("gmail", "v1", credentials=creds)
    #keywords = load_keywords("labels-keywords.json")
    keywords = load_rules_from_db()
    print(keywords)
    print(type(keywords))
    process_emails(service, keywords)
  except HttpError as error:
    print(f" An error occurred: {error}")


if __name__ == "__main__":
  main()

