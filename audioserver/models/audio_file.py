import sqlalchemy as sqla

from audioserver import db


class AudioFile(db.Base):
    """Model containing audio file metadata and mapping a UUID to file name."""

    __tablename__ = "audio_file"

    id = sqla.Column(sqla.Integer, primary_key=True)
    uuid = sqla.Column(sqla.String, nullable=False)
    name = sqla.Column(sqla.String, nullable=False)
    duration = sqla.Column(sqla.Float, nullable=False)
    mime_type = sqla.Column(sqla.String, nullable=False)
