
import shutil
import time
import os
import logging
import traceback
from datetime import datetime

from fastapi import FastAPI, Depends, UploadFile, File, Query, HTTPException
from fastapi.params import Form
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from migrations.database import SessionLocal
from migrations.models import Message
from typing import List, Optional

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()


# Dependency for getting a session
async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Error in session: {e}\n{traceback.format_exc()}")
            raise
        finally:
            await session.close()


# Pydantic models for request and response validation
class MessageCreate(BaseModel):
    client_id: str
    content: Optional[str] = None
    type_ms: str  # 'text', 'voice', 'video'
    media_file: Optional[UploadFile] = None


class MessageRead(BaseModel):
    client_id: str
    content: Optional[str]
    type: str
    media_path: Optional[str]
    created_at: datetime


@app.post("/messages/", response_model=MessageRead)
async def create_message(
        client_id: str = Form(...),
        type_ms: str = Form(...),
        content: Optional[str] = Form(None),
        media_file: Optional[UploadFile] = File(None),
        session: AsyncSession = Depends(get_session)
):
    media_path = None
    if media_file:
        try:
            media_path = await save_media_file(media_file, type_ms)
            logger.debug(f"Media file saved to: {media_path}")
        except Exception as e:
            logger.error(f"Failed to save media file: {e}\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail="Failed to save media file")

    try:
        db_message = Message(
            client_id=client_id,
            content=content,
            type=type_ms,
            media_path=media_path
        )
        session.add(db_message)
        await session.commit()
        await session.refresh(db_message)
        logger.debug(f"Message stored in database: {db_message}")
        return db_message
    except Exception as e:
        logger.error(f"Failed to create message: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to create message")


@app.get("/messages/", response_model=List[MessageRead])
async def get_messages(
    client_id: str = Form(...),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(10, ge=1, le=100),
    offset: int = 0
):
    result = await session.execute(
        select(Message)
        .filter_by(client_id=client_id)
        .offset(offset)
        .limit(limit)
    )
    messages = result.scalars().all()
    return messages


async def save_media_file(media_file: UploadFile, message_type: str) -> str:
    MEDIA_DIR = "media/"
    filename = f"{message_type}_{int(time.time())}_{media_file.filename}"
    media_path = os.path.join(MEDIA_DIR, filename)
    os.makedirs(MEDIA_DIR, exist_ok=True)
    try:
        with open(media_path, "wb") as f:
            shutil.copyfileobj(media_file.file, f)
        logger.debug(f"File {media_file.filename} saved at {media_path}")
        return media_path
    except Exception as e:
        logger.error(f"Error saving file {media_file.filename}: {e}\n{traceback.format_exc()}")
        raise
