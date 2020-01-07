from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


def connect(database_uri):
    Engine = create_engine(database_uri, echo=True)
    Session = sessionmaker(bind=Engine)

    return Session(), Engine
