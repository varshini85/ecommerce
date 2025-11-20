from dotenv import load_dotenv
load_dotenv(override=True)

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    raise RuntimeError("DATABASE_URL is not set.")

# Clean accidental quotes/spaces (VS Code or .env formatting issues)
DB_URL = DB_URL.strip().strip('"').strip("'")

engine = create_engine(DB_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_session = SessionLocal
