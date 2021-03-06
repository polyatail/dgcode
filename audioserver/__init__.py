import logging
import sys


formatter = logging.Formatter("%(asctime)s %(levelname).1s: %(message)s")
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)

log = logging.getLogger("audioserver")
log.setLevel(logging.DEBUG)
log.addHandler(stream_handler)
