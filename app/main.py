from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas, crud
from app.database import engine, get_db
import os

app = FastAPI(
    title="API de Películas",
    description="Una API REST para gestionar información de películas.",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=engine)
    db = next(get_db())
    
    if not db.query(models.Movie).first():
        crud.load_movies_from_csv(db)
    db.close()

@app.get("/movie", response_model=schemas.Movie, summary="Obtener una película por su ID")
def read_movie(id: int, db: Session = Depends(get_db)):
    """
    Retorna la información de una película específica dado su ID.
    """
    db_movie = crud.get_movie(db, movie_id=id)
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return db_movie

@app.get("/movies", response_model=List[schemas.Movie], summary="Listar películas ordenadas alfabéticamente")
def list_movies(
    total: int = 10,
    order: str = "asc",
    db: Session = Depends(get_db)
):
    """
    Lista películas, permitiendo especificar el número máximo de resultados y el orden alfabético.
    - **total**: Número máximo de películas a devolver (por defecto 10).
    - **order**: Orden alfabético (asc: ascendente, desc: descendente).
    """
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="El parámetro 'order' debe ser 'asc' o 'desc'")
    movies = crud.get_movies(db, total=total, order=order)
    return movies

@app.post("/movie", response_model=dict, status_code=status.HTTP_201_CREATED, summary="Agregar una nueva película")
def add_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    """
    Agrega una nueva película a la base de datos.
    El cuerpo de la petición debe contener el ID, nombre, género, estudio, puntuación y año de la película.
    """
    db_movie = crud.get_movie(db, movie_id=movie.id)
    if db_movie:
        raise HTTPException(status_code=400, detail="La película con este ID ya existe")
    crud.create_movie(db=db, movie=movie)
    return {"message": "La película fue creada con éxito"}