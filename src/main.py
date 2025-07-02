import asyncio
from logging import getLogger

from nio import AsyncClient, LoginError

from config import config
from connection import Connection
from utils import check_env

check_env()

client = AsyncClient(config.homeserver, config.username)
logger = getLogger(__name__)

async def main():
    res = await client.login(config.password, device_name="Recorder")

    if isinstance(res, LoginError):
        logger.info(f"Login failed: {res.message}")
        return

    connection = Connection(client, res.access_token)
    await connection.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt: Stopping the client.")