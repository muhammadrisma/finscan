import os
from dotenv import load_dotenv

from sqlalchemy import create_engine, Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProcessingLog(Base):
    __tablename__ = "processing_log"

    id = Column(String, primary_key=True)
    original_description = Column(String)
    agent_1_result = Column(String) # json result
    agent_2_result = Column(String) # json result
    agent_3_result = Column(String) # json result

class ResultLog(Base):
    __tablename__ = "result_log"

    id = Column(String, primary_key=True)
    original_description = Column(String)
    extracted_fish_name = Column(String)
    fish_name_english = Column(String)
    fish_name_latin = Column(String)
    flag = Column(Boolean)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 