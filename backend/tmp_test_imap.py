import imaplib
from datetime import datetime, timedelta

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login('testese2026@gmail.com', 'cgbtbpcyrgocpmbo')
mail.select('INBOX')

yesterday_imap = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
print(f"Searching SINCE {yesterday_imap}")
status, messages = mail.search(None, f'(SINCE "{yesterday_imap}")')

email_ids = messages[0].split()
print(f"Found {len(email_ids)} emails since yesterday")
print(email_ids)

mail.logout()
