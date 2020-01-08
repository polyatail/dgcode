import random
import uuid

from aiohttp import web
import mutagen

from audioserver.models import AudioFile, AudioFileClip, RandomSet


routes = web.RouteTableDef()


def filter_results(request):
    """Interpret a GET request, filtering by name and max duration.

    Parameters
    ----------
    request : `web.Request`

    Returns
    -------
    `sqlalchemy.orm.query.Query` of `AudioFile` objects, filtered by name and duration.
    """
    query = request.session.query(AudioFile)

    # support filtering by name, duration, and uuid
    if "name" in request.query:
        query = query.filter(AudioFile.name == request.query.get("name"))

    if "maxduration" in request.query:
        query = query.filter(AudioFile.duration <= request.query.get("maxduration"))

    return query


@routes.post("/post")
async def upload_handler(request):
    """Handle POST request to upload a new audio file.

    The file field name must be "file" in order for this to work. This is not in line with the spec
    per se, but as written there is no way to obtain the name of the file, since the spec just
    dumps the entire binary contents of the file in the POST.

    Parameters
    ----------
    request : `web.Request`

    Returns
    -------
    `web.Response` with status 400 if file not specified or invalid.
    """
    data = await request.post()

    file = data.get("file")

    if file is None:
        return web.Response(status=400)

    # get duration (e.g., 60 seconds) and file type (e.g., audio/mpeg)
    mut = mutagen.File(file.file)

    if mut is None:
        # mutagen couldn't identify the file type
        return web.Response(status=400)

    duration = mut.info.length
    mime_type = mut.mime[0]

    # generate a new UUID for this file
    new_uuid = uuid.uuid4().hex

    # store the file, associated with this UUID
    file.file.seek(0)
    request.storage.set_file_by_uuid(new_uuid, file.file)

    # create a new model for this file
    model = AudioFile(uuid=new_uuid, name=file.filename, duration=duration, mime_type=mime_type)
    request.session.add(model)
    request.session.commit()

    return web.json_response({"uuid": new_uuid})


@routes.get("/download")
async def download_handler(request):
    """Handle GET request to download an existing audio file by UUID.

    The UUID must get specified in the query string of the request.

    Parameters
    ----------
    request : `web.Request`

    Returns
    -------
    `web.Response` with status 400 if a uuid was not specified, and 404 if the uuid could not be
    found in either the SQL database or the file storage system.
    """
    uuid = request.query.get("uuid")

    if uuid is None:
        return web.Response(status=400)

    from audioserver.models import AudioFile

    result = request.session.query(AudioFile).filter_by(uuid=uuid).one_or_none()

    if result is None:
        return web.Response(status=404)

    body = request.storage.get_file_by_uuid(uuid)

    if body is None:
        return web.Response(status=404)

    return web.Response(body=body, headers={"Content-Type": result.mime_type})


@routes.get("/list")
async def list_handler(request):
    """Handle GET request to list the names of existing audio files.

    Allows filtering by "name" and "maxduration" when specified in the query string.

    Parameters
    ----------
    request : `web.Request`

    Returns
    -------
    `web.Response`
    """
    response = [result.name for result in filter_results(request)]

    return web.json_response(response)


@routes.get("/info")
async def info_handler(request):
    """Handle GET request to list metadata (e.g., name, duration) of existing audio files.

    Allows filtering by "name" and "maxduration" when specified in the query string.

    Parameters
    ----------
    request : `web.Request`

    Returns
    -------
    `web.Response`
    """
    response = []

    for result in filter_results(request):
        response.append(
            {
                "uuid": result.uuid,
                "name": result.name,
                "duration": result.duration,
                "mime_type": result.mime_type,
            }
        )

    return web.json_response(response)


@routes.get("/random_set")
async def random_set_handler(request):
    """Handle GET request to download a set of random audio clips from the corpus.

    If `uuid` is specified, download an existing set. Otherwise, generate a new set using the
    provided `number_of_clips` and `clip_length` parameters.

    Parameters
    ----------
    request : `web.Request`

    Returns
    -------
    `web.Response`
    """
    request_uuid = request.query.get("uuid")

    if request_uuid is not None:
        # fetch existing random set
        random_set = request.session.query(RandomSet).filter_by(uuid=request_uuid).one_or_none()

        if random_set is None:
            return web.Response(status=404)

        response_headers = {
            "Content-Type": "application/tar",
            "Content-Disposition": f"Attachment;filename={request_uuid}.tar",
        }

        return web.Response(
            body=random_set.generate_tarball(request.storage), headers=response_headers,
        )

    number_of_clips = int(request.query.get("number_of_clips"))
    clip_length = float(request.query.get("clip_length"))

    if number_of_clips is None or clip_length is None:
        return web.Response(status=400)

    # generate a new set
    clips_in_set = set()

    # fetch AudioFiles where duration > clip_length
    files_to_choose_from = (
        request.session.query(AudioFile).filter(AudioFile.duration >= clip_length).all()
    )

    # keep track of how many times we failed to generate a clip
    failures = 0

    while len(clips_in_set) < number_of_clips:
        # randomly select an AudioFile
        clip_file = random.choice(files_to_choose_from)

        # randomly select a starting position from [0, length - clip_length]
        clip_start = random.randrange(0, int(100 * (clip_file.duration - clip_length))) / 100.0
        clip_stop = clip_start + clip_length

        clip_params = (clip_file.id, clip_start, clip_stop)

        if clip_params in clips_in_set:
            failures += 1

            # there aren't enough clips in the corpus to satisfy the requested number_of_clips
            if failures == 5:
                break
        else:
            clips_in_set.add(clip_params)

    # create new AudioFileClips, using existing models when available
    clip_models = []

    for clip_file_id, clip_start, clip_stop in clips_in_set:
        model = (
            request.session.query(AudioFileClip)
            .filter_by(audio_file_id=clip_file_id, start=clip_start, stop=clip_stop)
            .one_or_none()
        )

        if model is None:
            # create new model
            model = AudioFileClip(audio_file_id=clip_file_id, start=clip_start, stop=clip_stop)
            request.session.add(model)
            request.session.commit()

        clip_models.append(model)

    # create a new RandomSet model
    new_uuid = uuid.uuid4().hex

    random_set = RandomSet(uuid=new_uuid, clips=clip_models)
    request.session.add(random_set)
    request.session.commit()

    response_headers = {
        "Content-Type": "application/tar",
        "Content-Disposition": f"Attachment;filename={new_uuid}.tar",
    }

    return web.Response(
        body=random_set.generate_tarball(request.storage).read(), headers=response_headers,
    )


def pass_parameters_factory(session, storage):
    """Create middleware that inserts the current SQL session and storage backend into a request."""

    @web.middleware
    async def pass_parameters(request, handler):
        request.session = session
        request.storage = storage

        return await handler(request)

    return pass_parameters
