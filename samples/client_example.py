import asyncio

from gama_client.base_client import GamaBaseClient


async def message_handler(message):
    print("received message:", message)


async def main():
    client = GamaBaseClient("localhost", 6868, message_handler)
    await client.connect(False)

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
