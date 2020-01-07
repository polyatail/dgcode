"""Classes that store audio files, indexed by UUID.

The idea is that every class in this file exposes the same interface, but stores audio files in a
different way. For example, local file storage, storage in redis, storage in S3, etc.
"""
import os

from audioserver.exceptions import AudioServerException


class LocalAudioStorage(object):
    """Store audio files locally, named by UUID."""

    def __init__(self, path):
        """Create a new instance of this storage backend.

        Parameters
        ----------
        path : `str`
            The complete path to the folder in which audio files are to be stored.
        """
        self.path = path

    def get_file_by_uuid(self, uuid):
        """Get the contents of an audio file by UUID.

        Parameters
        ----------
        uuid : `str`
            The unique identifier for the desired file.

        Returns
        -------
        `bytes`, raises `AudioServerException` if file not found.
        """
        path = os.path.join(self.path, uuid)

        if not os.path.isfile(path):
            raise AudioServerException(f"File for {uuid} was not found")

        with open(path, "rb") as fp:
            return fp.read()

    def set_file_by_uuid(self, uuid, file_object, force=False):
        """Store the contents of an audio file by UUID.

        Parameters
        ----------
        uuid : `str`
            The unique identifier for the desired file.
        file_object : a file-like object
            That which contains the audio file to be written.
        force : `bool`
            If True, overwrite existing file with the same UUID.

        Returns
        -------
        `None`, raises `AudioServerException` if file already exists and `force` is False.
        """
        path = os.path.join(self.path, uuid)

        if os.path.isfile(path) and not force:
            raise AudioServerException(f"File for {uuid} already exists")

        with open(path, "wb") as fp:
            fp.write(file_object.read())
