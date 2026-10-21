from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

class Base(DeclarativeBase):
    pass

def criar_engine():
    engine = create_engine("sqlite:///biblioteca.db", echo=False)
    return engine, sessionmaker(bind=engine)()

SessionLocal = sessionmaker(bind=criar_engine())
session = Session()