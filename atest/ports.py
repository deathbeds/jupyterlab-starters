""" get a random port
"""

import socket
import time
import urllib.request

from robot.api import logger


def get_unused_port():
    """Get an unused port by trying to listen to any random port.

    Probably could introduce race conditions if inside a tight loop.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 0))
    sock.listen(1)
    port = sock.getsockname()[1]
    sock.close()
    return port


def wait_for_url_status(
    url: str, status_code: int, interval_sec: float = 0.1, attempts: int = 100
) -> bool:
    """Attempt to fetch from the URL until, or raise an"""
    response = None

    for i in range(attempts):
        try:
            response = urllib.request.urlopen(url)
            if response.status == status_code:
                break
            logger.debug(response.status)
        except Exception:
            logger.debug(Exception)
        time.sleep(interval_sec)

    if not response or response.status != status_code:
        raise RuntimeError(
            f"{url} did return {status_code} within {interval_sec * attempts}s"
        )

    return True
