from sqlalchemy import Column, Integer, String
from app.database import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    film = Column(String, index=True)
    genre = Column(String)
    studio = Column(String)
    score = Column(Integer)
    year = Column(Integer)