import json

from aiohttp import web

from audioserver.models import AudioFile
from audioserver.utils import filter_results


routes = web.RouteTableDef()


@routes.post("/post")
async def upload_handler(request):
    pass


@routes.get("/download")
async def download_handler(request):
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
    response = [result.name for result in filter_results(request)]

    return web.json_response(response)


@routes.get("/info")
async def info_handler(request):
    response = []

    for result in filter_results(request):
        response.append({"uuid": result.uuid, "name": result.name, "duration": result.duration})

    return web.json_response(response)


def pass_parameters_factory(session, storage):
    @web.middleware
    async def pass_parameters(request, handler):
        request.session = session
        request.storage = storage

        return await handler(request)

    return pass_parameters
