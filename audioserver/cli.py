import logging
import os

from aiohttp import web
import click

from audioserver import api, log
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

    # set path to database
    from audioserver import config

    config.SQLALCHEMY_DB_URI = f"sqlite:///{os.path.join(path, 'db.sqlite3')}"

    # create tables
    from audioserver import db, models

    try:
        log.info(f"cli.init: creating empty tables")
        db.Base.metadata.create_all(db.Engine)
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

    # set path to database
    from audioserver import config

    config.SQLALCHEMY_DB_URI = f"sqlite:///{os.path.join(path, 'db.sqlite3')}"

    # create a file storage instance
    storage = LocalAudioStorage(path)

    # setup middleware, app, and routes
    from audioserver import db

    middlewares = [api.pass_parameters_factory(db.session, storage)]
    app = web.Application(client_max_size=10 * 1024 ** 2, middlewares=middlewares)
    app.add_routes(api.routes)

    try:
        log.info(f"cli.run: listening on port {port}")
        web.run_app(app, port=port)
    except KeyboardInterrupt:
        log.info(f"cli.run: caught ctrl+c, cleaning up and quitting...")
