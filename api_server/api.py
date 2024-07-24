from fastapi import FastAPI
import asyncpg
import redis.asyncio as aioredis
from contextlib import asynccontextmanager
from models.message import Message

app = FastAPI()

# Configuration
REDIS_URL = "redis://redis:6379/0"
DATABASE_URL = "postgresql://postgres:postgres@db/postgres"


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool, redis
    # Initialize resources
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    redis = aioredis.from_url(REDIS_URL)

    yield

    # Cleanup resources
    await db_pool.close()
    await redis.close()


app.router.lifespan_context = lifespan


@app.post("/send_message/")
async def send_message(message: Message):
    # Process the message (e.g., store in database, send to message processor)
    async with db_pool.acquire() as connection:
        await connection.execute(
            "INSERT INTO messages (content, type) VALUES ($1, $2)",
            message.content, message.type
        )
    return {"status": "Message received"}


@app.get("/get_history/")
async def get_history(limit: int = 10, offset: int = 0):
    # Retrieve message history
    async with db_pool.acquire() as connection:
        rows = await connection.fetch(
            "SELECT * FROM messages ORDER BY created_at DESC LIMIT $1 OFFSET $2",
            limit, offset
        )
    return [dict(row) for row in rows]
