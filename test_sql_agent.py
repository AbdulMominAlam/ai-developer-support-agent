import asyncio

from agent import process_message


async def main():
    result = await process_message(
        "Which account has the most support tickets?"
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())