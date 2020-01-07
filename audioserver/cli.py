import click

from audioserver import log
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


@audioserver_cli.command("server", help="Launch server")
@click.pass_context
@click.option("--port", type=int, default=5000, help="Port to listen on")
@click.option(
    "--path",
    type=click.Path(resolve_path=True),
    default="files/",
    help="Path to audio file storage (will create if does not exist)",
)
def server(ctx, port, path):
    pass
