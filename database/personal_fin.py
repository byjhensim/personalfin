import settings
from datetime import datetime
from sqlalchemy import Integer,Numeric, Column, DateTime,Date, String
from database import database

personalfin = database(settings.PERSONALFIN_DSN)

class StockTransaction(personalfin.TableBase):
    __tablename__="stock_transaction"

    id = Column(Integer, primary_key=True)
    transaction_date = Column(Date)
    transaction_type = Column(String(16))
    stock= Column(String(4))
    stock_desc = Column(String(128))
    volume=Column(Numeric)
    price=Column(Integer)
    amount=Column(Numeric)
    curr = Column(String(4))
    security = Column(String(32))
    created_at = Column(DateTime, default=datetime.now)
    


