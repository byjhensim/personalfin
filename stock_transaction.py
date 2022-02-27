"""
This code is generally to collect trading information from personal email and populate the data into database
The data is in pdf form residing in personal email.
Final output is information like what stock being bought or sold, for how many and how much.
"""
import os
import settings
import re
import pdfplumber
from prefect import Flow, task, Parameter, unmapped
from prefect.run_configs import LocalRun
from file_hosting import DropboxUtility
from datetime import datetime
from extractor.gmail import fetch_mail_attachment, search_mail
from database.personal_fin import personalfin, StockTransaction


@task
def search_mail_id(subject, since):
    mail_ids = search_mail(subject=subject,since=since)
    return mail_ids

@task
def extract_attachment_pdf(mail_id):    
    pdf_path = fetch_mail_attachment(mail_id)    
    return pdf_path       

@task
def upload_pdf_to_dropbox(file_path, dropbox_path):
    if file_path:      
        dbx = DropboxUtility(settings.DROPBOX_TOKEN)
        file_to = dropbox_path + '/' + os.path.basename(file_path)    
        with open(file_path,'rb') as f:
            res = dbx.upload_file(f.read(), file_to)
        os.remove(file_path)
        return res
    

@task
def parse_stock_transaction(file_paths):
    transactions = []    
    for file_path in file_paths:
        if file_path:        
            with pdfplumber.open(file_path) as pdf:
                raw_text = pdf.pages[0].extract_text()     
                pattern = re.compile(r'RG (.*) - (.*) I (.*) (.*) (.*) (.*) (.*)')    
            for search in pattern.findall(raw_text):
                transaction ={
                'date': re.findall(r'\d+', file_path)[0],
                'stock':search[0],
                'stock_desc':search[1],
                'volume': int(search[3].replace(',','')),
                'price': int(search[4].replace(',','')),
                'buy':int(search[5].replace(',','')),
                'sell':int(search[6].replace(',',''))
                }
                transactions.append(transaction)   
        
    return transactions

@task
def load_transaction(transactions):
    bulk = []
    for transaction in transactions:
        if transaction['buy'] != 0:
            bulk.append(StockTransaction(
                transaction_date=datetime.strptime(transaction['date'],'%Y%m%d').date(),
                transaction_type='buy',
                stock=transaction['stock'],
                stock_desc=transaction['stock_desc'],
                volume=transaction['volume'],
                price=transaction['price'],
                amount=transaction['buy'],
                curr='IDR',
                security='Sinarmas'
            ))
        else:
            bulk.append(StockTransaction(
                transaction_date=datetime.strptime(transaction['date'],'%Y%m%d').date(),
                transaction_type='sell',
                stock=transaction['stock'],
                stock_desc=transaction['stock_desc'],
                volume=transaction['volume'],
                price=transaction['price'],
                amount=transaction['sell'],
                curr='IDR',
                security='Sinarmas'
            ))
    personalfin.session.bulk_save_objects(bulk)
    personalfin.session.commit()



with Flow("StockSinarmasTrading-ETL") as flow:
    mail_subject = Parameter('mail_subject')
    since = Parameter('since')
    dropbox_path = Parameter('dropbox_path')
    mail_id = search_mail_id(mail_subject, since)
    pdf_path = extract_attachment_pdf.map(mail_id)
    transaction = parse_stock_transaction(pdf_path)
    load_ref = load_transaction(transaction)
    upload_ref = upload_pdf_to_dropbox.map(file_path=pdf_path, dropbox_path=unmapped(dropbox_path), upstream_tasks=[transaction])
    
flow.run_config=LocalRun(
    working_dir=os.path.abspath(os.path.dirname(__file__)),
    labels=['personalfin']
    )