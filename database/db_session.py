# # load env
# from dotenv import load_dotenv
# load_dotenv(override=True)

# import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, Session

# DB_URL = os.getenv('DATABASE_URL')
# engine = create_engine(DB_URL)
# SessionLocal = sessionmaker(bind=engine,expire_on_commit=False)
# db_session = Session

# def get_session():
#     session = SessionLocal(bind=engine)
#     try:
#         yield session
#     finally:
#         session.close()
# database/db_session.py

# Load env file locally (ignored in Azure App Service)
from dotenv import load_dotenv
load_dotenv(override=True)

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Read DATABASE_URL
DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    raise RuntimeError(
        "❌ DATABASE_URL is not set. "
        "Set it in Azure App Service → Configuration → Application settings."
    )

# SQLAlchemy engine + session factory
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for models
Base = declarative_base()

# Backward compatibility: keep db_session import working
db_session = SessionLocal

# Dependency for FastAPI routes
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
