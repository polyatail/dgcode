from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Engine = create_engine("sqlite:///:memory:", echo=True)
Session = sessionmaker(bind=Engine)
Base = declarative_base()

session = Session()
