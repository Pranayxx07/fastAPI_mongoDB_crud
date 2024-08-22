from pydantic import BaseModel, HttpUrl
from typing import Optional

class Movie(BaseModel):
    name: str
    img: HttpUrl
    summary: Optional[str] = None
