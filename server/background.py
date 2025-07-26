import asyncio

from server.crud import delete_cache
from server.db import engine


async def listen_notifications() -> None:
    async with engine.connect() as conn:
        raw_conn = await conn.get_raw_connection()
        await raw_conn.driver_connection.add_listener(
            "category",
            listener_callback,
        )

        print("Listening on channel 'my_channel'...")
        while True:
            await asyncio.sleep(1)


@delete_cache
async def listener_callback(conn, pid, channel, payload):
    print(f"Notification received on '{channel}': {payload}")
