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


class AudioFileClip(db.Base):
    """Model describing a segment of an AudioFile."""

    __tablename__ = "audio_file_clip"

    id = sqla.Column(sqla.Integer, primary_key=True)
    start = sqla.Column(sqla.Float, nullable=False)
    stop = sqla.Column(sqla.Float, nullable=False)

    # relationships
    audio_file_id = sqla.Column(sqla.Integer, sqla.ForeignKey("audio_file.id"), nullable=False)
    audio_file = sqla.orm.relationship("AudioFile")

    def get_wav(self, storage_backend):
        """Get this clip in WAV format using the provided storage backend.

        Parameters
        ----------
        storage_backend : e.g. `audioserver.storage.LocalAudioStorage`

        Returns
        -------
        `io.BytesIO` containing the WAV file
        """
        return storage_backend.get_wav_by_uuid(self.audio_file.uuid, self.start, self.stop)
