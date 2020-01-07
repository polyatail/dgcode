import sqlalchemy as sqla

from audioserver import db


class AudioFile(db.Base):
    __tablename__ = "audio_file"

    id = sqla.Column(sqla.Integer, primary_key=True)
    uuid = sqla.Column(sqla.String, nullable=False)
    filename = sqla.Column(sqla.String, nullable=False)
    duration = sqla.Column(sqla.Integer, nullable=False)
