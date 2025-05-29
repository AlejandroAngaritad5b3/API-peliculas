from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app import models, crud
import pandas as pd
import os

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def setup_function(function):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    csv_file_path = "data/movies.csv"
    if os.path.exists(csv_file_path):
        df = pd.read_csv(csv_file_path)
        for index, row in df.iterrows():
            movie = models.Movie(
                id=row['ID'],
                film=row['Film'],
                genre=row['Genre'],
                studio=row['Studio'],
                score=row['Score'],
                year=row['Year']
            )
            db.add(movie)
        db.commit()
    db.close()

def teardown_function(function):
    Base.metadata.drop_all(bind=engine)

def test_read_movie():
    response = client.get("/movie?id=7")
    assert response.status_code == 200
    assert response.json() == {
        "id": 7,
        "film": "WALL-E",
        "genre": "Animation",
        "studio": "Disney",
        "score": 89,
        "year": 2008
    }

def test_read_nonexistent_movie():
    response = client.get("/movie?id=999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Película no encontrada"}

def test_list_movies_asc():
    response = client.get("/movies?total=3&order=asc")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["film"] == "(500) Days of Summer"
    assert data[1]["film"] == "27 Dresses"
    assert data[2]["film"] == "A Dangerous Method"

def test_list_movies_desc():
    response = client.get("/movies?total=3&order=desc")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["film"] == "Zack and Miri Make a Porno"
    assert data[1]["film"] == "Youth in Revolt"
    assert data[2]["film"] == "You Will Meet a Tall Dark Stranger"

def test_list_movies_invalid_order():
    response = client.get("/movies?total=3&order=invalid")
    assert response.status_code == 400
    assert response.json() == {"detail": "El parámetro 'order' debe ser 'asc' o 'desc'"}

def test_add_movie():
    new_movie_data = {
        "id": 78,
        "film": "Parasite",
        "genre": "Drama",
        "studio": "Barunson E&A",
        "score": 97,
        "year": 2019
    }
    response = client.post("/movie", json=new_movie_data)
    assert response.status_code == 201
    assert response.json() == {"message": "La película fue creada con éxito"}

    get_response = client.get("/movie?id=78")
    assert get_response.status_code == 200
    assert get_response.json()["film"] == "Parasite"

def test_add_existing_movie():
    existing_movie_data = {
        "id": 1,
        "film": "Another Movie",
        "genre": "Comedy",
        "studio": "Studio X",
        "score": 80,
        "year": 2020
    }
    response = client.post("/movie", json=existing_movie_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "La película con este ID ya existe"}