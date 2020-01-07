import os


SQLALCHEMY_DB_URI = os.environ.get("SQLALCHEMY_DB_URI", "sqlite:///:memory:")
