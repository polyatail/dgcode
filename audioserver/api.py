import uuid

from aiohttp import web
import mutagen

from audioserver.models import AudioFile


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


def pass_parameters_factory(session, storage):
    """Create middleware that inserts the current SQL session and storage backend into a request."""

    @web.middleware
    async def pass_parameters(request, handler):
        request.session = session
        request.storage = storage

        return await handler(request)

    return pass_parameters
