from pydantic import BaseModel, HttpUrl
from typing import Optional



class Movie(BaseModel):
    name: str
    img: Optional[str] = None
    summary: Optional[str] = None





class GetMovie(BaseModel):
    id : str
    name: str
    img: str
    summary: Optional[str] = None