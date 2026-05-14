from src.gmail_client import GmailClient

print("Connecting to Gmail...")
gmail = GmailClient()

print("Searching for emails with attachments...")
emails = gmail.search_emails("has:attachment", max_results=5)

print(f"Found {len(emails)} emails with attachments\n")
for email in emails:
    print(f"From: {email['From']}")
    print(f"Subject: {email['subject']}")
    print(f"Date: {email['date']}")
    for att in email['date']:
        print(f" Attachment: {att['filename']}")
    print()