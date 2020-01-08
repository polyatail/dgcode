from io import BytesIO
import os
import tarfile

import sqlalchemy as sqla

from audioserver import db


random_set_clips = sqla.Table(
    "random_set_clips",
    db.Base.metadata,
    sqla.Column("random_set_id", sqla.Integer, sqla.ForeignKey("random_set.id")),
    sqla.Column("audio_file_clip_id", sqla.Integer, sqla.ForeignKey("audio_file_clip.id")),
)


class RandomSet(db.Base):
    """Model describing a random set of audio clips from the database."""

    __tablename__ = "random_set"

    id = sqla.Column(sqla.Integer, primary_key=True)
    uuid = sqla.Column(sqla.String, nullable=False)
    clips = sqla.orm.relationship("AudioFileClip", secondary="random_set_clips")

    def generate_tarball(self, storage_backend):
        """Generate a tarball containing all audio clips in WAV format.

        Parameters
        ----------
        storage_backend : e.g. `audioserver.storage.LocalAudioStorage`

        Returns
        -------
        `io.BytesIO` containing the tarball, uncompressed.
        """
        buf = BytesIO()

        with tarfile.open(mode="w", fileobj=buf) as tar:
            for clip in self.clips:
                wav = clip.get_wav(storage_backend)

                name, ext = os.path.splitext(clip.audio_file.name)

                info = tarfile.TarInfo(name=f"{name}_{clip.start}_{clip.stop}.wav")
                info.size = wav.getbuffer().nbytes
                tar.addfile(info, wav)

        buf.seek(0)

        return buf
