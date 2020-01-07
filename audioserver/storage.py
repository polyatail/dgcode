"""Classes that store audio files, indexed by UUID.

The idea is that every class in this file exposes the same interface, but stores audio files in a
different way. For example, local file storage, storage in redis, storage in S3, etc.
"""


class LocalAudioStorage(object):
    """Store audio files locally, named by UUID."""

    def __init__(self, path):
        pass

    def get_file_by_uuid(self, uuid):
        pass

    def set_file_by_uuid(self, uuid, file_object):
        pass
