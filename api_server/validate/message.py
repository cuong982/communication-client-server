from pydantic import BaseModel


class Message(BaseModel):
    content: str
    type: str  # "text", "voice", "video"
