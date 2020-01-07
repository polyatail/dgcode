def validate_audio_file(file_path):
    pass


def filter_results(request):
    from audioserver.models import AudioFile

    query = request.session.query(AudioFile)

    # support filtering by name, duration, and uuid
    if "name" in request.query:
        query = query.filter(AudioFile.name == request.query.get("name"))

    if "maxduration" in request.query:
        query = query.filter(AudioFile.duration <= request.query.get("maxduration"))

    return query
