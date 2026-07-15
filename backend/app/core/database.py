"""
Database connection setup.

We use SQLAlchemy as the ORM, connecting to MySQL via the PyMySQL
driver.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Example: mysql+pymysql://root:yourpassword@localhost:3306/hcp_crm
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:root@localhost:3306/hcp_crm")

# pool_pre_ping avoids the classic "MySQL server has gone away" error
# on long-idle connections — MySQL closes idle connections after a
# timeout, unlike Postgres, so this check is MySQL-specific good practice.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency — yields a DB session per request and
    always closes it afterward, even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
