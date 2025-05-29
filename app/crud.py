import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from app import models, schemas
import os

def get_movie(db: Session, movie_id: int):
    return db.query(models.Movie).filter(models.Movie.id == movie_id).first()

def get_movies(db: Session, total: int = 10, order: str = "asc"):
    if order == "asc":
        return db.query(models.Movie).order_by(asc(models.Movie.film)).limit(total).all()
    elif order == "desc":
        return db.query(models.Movie).order_by(desc(models.Movie.film)).limit(total).all()
    return []

def create_movie(db: Session, movie: schemas.MovieCreate):
    db_movie = models.Movie(
        id=movie.id,
        film=movie.film,
        genre=movie.genre,
        studio=movie.studio,
        score=movie.score,
        year=movie.year
    )
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)

    return db_movie

def load_movies_from_csv(db: Session, csv_file_path: str = "data/movies.csv"):
    if not os.path.exists(csv_file_path):
        print(f"Warning: file csv not found {csv_file_path}. Initial data wont be loaded.")
        return

    try:
        df = pd.read_csv(csv_file_path)
        for index, row in df.iterrows():
            existing_movie = db.query(models.Movie).filter(models.Movie.id == row['ID']).first()
            if not existing_movie:
                movie = schemas.MovieCreate(
                    id=row['ID'],
                    film=row['Film'],
                    genre=row['Genre'],
                    studio=row['Studio'],
                    score=row['Score'],
                    year=row['Year']
                )
                create_movie(db=db, movie=movie)
        print("Movie data loaded from CSV.")
    except Exception as e:
        print(f"Error to load data from CSV: {e}")