from pydantic import BaseModel, Field
from typing import Optional

class MovieBase(BaseModel):
    film: str
    genre: str
    studio: str
    score: int
    year: int

class MovieCreate(MovieBase):
    id: int

class MovieUpdate(BaseModel):
    film: Optional[str] = None
    genre: Optional[str] = None
    studio: Optional[str] = None
    score: Optional[int] = None
    year: Optional[int] = None

class Movie(MovieBase):
    id: int

    class Config:
        orm_mode = True