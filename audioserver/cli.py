import logging
import os

from aiohttp import web
import click

from audioserver import api, db, log
from audioserver.exceptions import AudioServerException
from audioserver.storage import LocalAudioStorage
from audioserver.version import __version__


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__)
@click.option("-v", "--verbose", count=True)
@click.pass_context
def audioserver_cli(ctx, verbose):
    if verbose == 0:
        log.setLevel(logging.WARNING)
    elif verbose == 1:
        log.setLevel(logging.INFO)
    elif verbose >= 2:
        log.setLevel(logging.DEBUG)


@audioserver_cli.command("init", help="Initialize empty database")
@click.pass_context
@click.option(
    "--path",
    type=click.Path(resolve_path=True),
    default="files/",
    help="Path to audio file storage (will create if does not exist)",
)
def init(ctx, path):
    if not os.path.exists(path):
        os.mkdir(path)
    elif not os.path.isdir(path):
        raise AudioServerException("Path exists and is not a directory")

    session, engine = db.connect(f"sqlite:///{os.path.join(path, 'db.sqlite3')}")

    # create tables
    from audioserver import models  # noqa

    try:
        log.info(f"cli.init: creating empty tables")
        db.Base.metadata.create_all(engine)
    except KeyboardInterrupt:
        log.info(f"cli.init: caught ctrl+c, cleaning up and quitting...")


@audioserver_cli.command("run", help="Launch server")
@click.pass_context
@click.option("--port", type=int, default=5000, help="Port to listen on")
@click.option(
    "--path",
    type=click.Path(resolve_path=True),
    default="files/",
    help="Path to audio file storage (must exist and contain a valid database)",
)
def run(ctx, port, path):
    if not os.path.isdir(path):
        raise AudioServerException("Path does not exist or is not a directory")

    # connect to the database
    session, _ = db.connect(f"sqlite:///{os.path.join(path, 'db.sqlite3')}")

    # create a file storage instance
    storage = LocalAudioStorage(path)

    # from audioserver.models import AudioFile, AudioFileClip, RandomSet
    # import ipdb

    # ipdb.set_trace()

    # setup middleware, app, and routes
    middlewares = [api.pass_parameters_factory(session, storage)]
    app = web.Application(client_max_size=10 * 1024 ** 2, middlewares=middlewares)
    app.add_routes(api.routes)

    try:
        log.info(f"cli.run: listening on port {port}")
        web.run_app(app, port=port, access_log=log)
    except KeyboardInterrupt:
        log.info(f"cli.run: caught ctrl+c, cleaning up and quitting...")
