from logging import getLogger

logger = getLogger(__name__)

def check_env():
    from config import config

    logger.info("ENV HOMESERVER=%s", config.homeserver)
    logger.info("ENV USERNAME=%s", config.username)
    logger.debug("ENV PASSWORD=%s", config.password)

    if not config.homeserver:
        raise ValueError("HOMESERVER is not set in the environment variables.")
    if not config.username:
        raise ValueError("USERNAME is not set in the environment variables.")
    if not config.password:
        raise ValueError("PASSWORD is not set in the environment variables.")