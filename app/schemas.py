from pydantic import BaseModel

class MovieBase(BaseModel):
    film: str
    genre: str
    studio: str
    score: int
    year: int

class MovieCreate(MovieBase):
    id: int 

class Movie(MovieBase):
    id: int

    class Config:
        orm_mode = True