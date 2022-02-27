import os
from dotenv import load_dotenv

##Setting up configuration variable
base_dir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(base_dir,'.env'))

GMAIL_HOST = os.environ.get('GMAIL_HOST')
GMAIL_USER = os.environ.get('GMAIL_USER')
GMAIL_SECRET = os.environ.get('GMAIL_SECRET')
DROPBOX_TOKEN = os.environ.get('DROPBOX_TOKEN')
MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_HOST = os.environ.get('MYSQL_HOST')
MYSQL_PASS = os.environ.get('MYSQL_PASS')
MYSQL_PORT = 3306
PERSONALFIN_DSN = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/personalfin"