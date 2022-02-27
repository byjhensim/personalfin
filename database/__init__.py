from database.base import BaseDatabase

def database(dsn:str) -> BaseDatabase:
    return BaseDatabase(dsn)