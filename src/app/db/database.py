import os
import pytz

from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Boolean, ForeignKey, Integer, DateTime, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_jakarta_time():
    jakarta_tz = pytz.timezone('Asia/Jakarta')
    return datetime.now(jakarta_tz)

class ProcessingLog(Base):
    __tablename__ = "processing_log"

    id = Column(Integer, Sequence('processing_log_id_seq'), primary_key=True)
    no_peb = Column(String)
    no_seri = Column(String)
    original_description = Column(String)
    agent_1_result = Column(String) # json result
    agent_2_result = Column(String) # json result
    agent_3_result = Column(String) # json result

class ResultLog(Base):
    __tablename__ = "result_log"

    id = Column(Integer, Sequence('result_log_id_seq'), primary_key=True)
    no_peb = Column(String)
    no_seri = Column(String)
    original_description = Column(String)
    extracted_fish_name = Column(String)
    fish_name_english = Column(String)
    fish_name_latin = Column(String)
    flag = Column(Boolean)
    from_cache = Column(Boolean, default=False)

class CacheLog(Base):
    __tablename__ = "cache_log"
    id = Column(Integer, Sequence('cache_log_id_seq'), primary_key=True)
    extracted_fish_name = Column(String, unique=True, index=True)
    fish_name_english = Column(String)
    fish_name_latin = Column(String)
    result_log_id = Column(Integer, ForeignKey("result_log.id"))

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(DateTime, primary_key=True, default=get_jakarta_time)
    total_processing_logs = Column(Integer, default=0)
    total_result_logs = Column(Integer, default=0)
    total_cache_logs = Column(Integer, default=0)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 