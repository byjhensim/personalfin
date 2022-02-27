from fileinput import filename
import settings
import re
import imaplib
import os
from email.parser import BytesParser
from datetime import date, timedelta
from pathlib import Path


def _create_connection(mailbox='inbox'):
    mail = imaplib.IMAP4_SSL(settings.GMAIL_HOST)
    mail.login(settings.GMAIL_USER,settings.GMAIL_SECRET)
    mail.select(mailbox)
    return mail

def _capture_date(filename) -> str:
    date_found = re.findall(r'-(\d+) ',filename)
    return date_found[0]

def _capture_criteria(**kwargs):
    criteria = ''
    criteria_list = {
        'sender': 'FROM',
        'subject': 'SUBJECT',
        'since':'SENTSINCE'
    }
    for key,value in kwargs.items():
        if type(value) == str:
            criteria += criteria_list[key] + " " + f'"{value}"' + " "
        if key == 'since':
            since_date = (date.today() - timedelta(value)).strftime("%d-%b-%Y")
            criteria += criteria_list[key] + " " + since_date + " "
    
    return f'({criteria[:-1]})'
    
def search_mail(**kwargs):
    session = _create_connection()
    criteria = _capture_criteria(**kwargs)
    with session:
        ids = session.search(None, criteria)[1][0].split()
    
    return [str(int(id)) for id in ids]

def fetch_mail_attachment(mail_id):
    session = _create_connection()    
    Path("temp").mkdir(parents=True, exist_ok=True)
    with session:
        res, raw = session.fetch(mail_id, ('RFC822'))
        if res == 'OK':
            email_content = BytesParser().parsebytes(raw[0][1])
            if email_content.is_multipart():
                for part in email_content.walk():
                    if part.get_content_type() == 'application/octet-stream':
                        file_name = "sinarmas_transaction" + _capture_date(part.get_filename()) + ".pdf"
                        file_path = os.path.join("temp",file_name)                        
                        with open(file_path,'wb') as f:
                            f.write(part.get_payload(decode=True))
                        return file_path

    
