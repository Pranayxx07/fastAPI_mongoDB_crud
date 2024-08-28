from pydantic import BaseModel, HttpUrl
from typing import Dict, Optional



class Movie(BaseModel):
    name: str
    img: Optional[Dict[str, str]] = None
    summary: Optional[str] = None





class GetMovie(BaseModel):
    id : str
    name: str
    img: Optional[Dict[str, str]] = None
    summary: Optional[str] = None