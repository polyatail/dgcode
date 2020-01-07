from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from audioserver.config import SQLALCHEMY_DB_URI


Engine = create_engine(SQLALCHEMY_DB_URI, echo=True)
Session = sessionmaker(bind=Engine)
Base = declarative_base()

session = Session()
