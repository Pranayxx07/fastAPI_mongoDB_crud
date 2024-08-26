from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import HttpUrl
from schemas import Movie
from fastapi.encoders import jsonable_encoder
from database.dbconnection import movie_collection
from bson import ObjectId
from common import movie_helper

routs = APIRouter()



@routs.post("/movies/", response_model=Movie)
async def create_movie(movie: Movie):
    try:
        movie = jsonable_encoder(movie)
        new_movie = await movie_collection.insert_one(movie)
        print(f"Inserted Movie ID: {new_movie.inserted_id}")
        created_movie = await movie_collection.find_one({"_id": new_movie.inserted_id})
        return movie_helper(created_movie)
    except Exception as e:
        print(f"Error: {e}")  # Log any errors
        raise HTTPException(status_code=500, detail="An error occurred while creating the movie.")



@routs.get("/get_all_movies/", response_model=List[Movie])
async def get_movies():
    movies = []
    async for movie in movie_collection.find():
        movies.append(movie_helper(movie))
    return movies


@routs.get("/get_movies/{id}", response_model=Movie)
async def get_movie(id: str):
    movie = await movie_collection.find_one({"_id": ObjectId(id)})
    if movie:
        return movie_helper(movie)
    raise HTTPException(status_code=404, detail="Movie not found")


@routs.put("/update_movies/{id}", response_model=Movie)
async def update_movie(id: str, movie: Movie):
    movie_data = movie.model_dump()

    movie_data['img'] = str(movie_data['img'])

    movie_data = {k: v for k, v in movie_data.items() if v is not None}
    update_result = await movie_collection.update_one({"_id": ObjectId(id)}, {"$set": movie_data})
    if update_result.modified_count == 1:
        updated_movie = await movie_collection.find_one({"_id": ObjectId(id)})
        if updated_movie:
            return movie_helper(updated_movie)

    existing_movie = await movie_collection.find_one({"_id": ObjectId(id)})
    if existing_movie:
        return movie_helper(existing_movie)

    raise HTTPException(status_code=404, detail="Movie not found")


@routs.delete("/delete_movies/{id}")
async def delete_movie(id: str):
    delete_result = await movie_collection.delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"status": "Movie deleted"}


