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

@app.patch("/movie/{movie_id}", response_model=schemas.Movie, summary="Actualizar parcialmente una película")
def update_movie_endpoint(movie_id: int, movie_update: schemas.MovieUpdate, db: Session = Depends(get_db)):
    """
    Actualiza la información de una película existente dado su ID.
    Los campos no proporcionados en el cuerpo de la petición no serán modificados.
    """
    db_movie = crud.get_movie(db, movie_id=movie_id)
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    
    updated_movie = crud.update_movie(db, movie_id=movie_id, movie_update=movie_update)
    return updated_movie

@app.put("/movie/{movie_id}", response_model=schemas.Movie, summary="Actualizar completamente una película")
def update_movie_full_endpoint(movie_id: int, movie: schemas.MovieBase, db: Session = Depends(get_db)):
    db_movie = crud.get_movie(db, movie_id=movie_id)
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    movie_update_data = schemas.MovieUpdate(**movie.dict()) 
    updated_movie = crud.update_movie(db, movie_id=movie_id, movie_update=movie_update_data)
    return updated_movie


@app.delete("/movie/{movie_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar una película")
def delete_movie_endpoint(movie_id: int, db: Session = Depends(get_db)):
    """
    Elimina una película de la base de datos dado su ID.
    """
    success = crud.delete_movie(db, movie_id=movie_id)
    if not success:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return