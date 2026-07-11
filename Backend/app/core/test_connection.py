import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import certifi

async def main():
    uri = "mongodb+srv://selva00611_db_user:NZ80R2Ktr7KruC7D@cluster0.9zhsstb.mongodb.net/glof_sentinel?retryWrites=true&w=majority&appName=Cluster0"

    client = AsyncIOMotorClient(
        uri,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=10000,
    )

    try:
        await client.admin.command("ping")
        print("✅ MongoDB Connected!")

        dbs = await client.list_database_names()
        print("Databases:", dbs)

    except Exception as e:
        print("❌ Connection Failed")
        print(type(e).__name__)
        print(e)

asyncio.run(main())