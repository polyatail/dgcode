from aiohttp import web


routes = web.RouteTableDef()


@routes.post("/post")
async def upload_handler(request):
    pass


@routes.get("/download")
async def download_handler(request):
    pass


@routes.get("/list")
async def list_handler(request):
    pass


@routes.get("/info")
async def info_handler(request):
    pass


def pass_parameters_factory(session, storage):
    @web.middleware
    async def pass_parameters(request, handler):
        request.session = session
        request.storage = storage

        return await handler(request)

    return pass_parameters
