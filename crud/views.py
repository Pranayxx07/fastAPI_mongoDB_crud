import logging
from typing import List
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import HttpUrl
from schemas import GetMovie, Movie
from fastapi.encoders import jsonable_encoder
from database.dbconnection import movie_collection
from bson import ObjectId
from common import is_allowed_file, movie_helper, save_image
import os

routs = APIRouter()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@routs.post("/movies/", response_model=Movie)
async def create_movie(movie_name,movie_summary,img: UploadFile = File(...)):
    
    try:
        movie = {
                "name": movie_name,
                "summary": movie_summary
                 }
        
        if not is_allowed_file(img.filename):
            raise HTTPException(status_code=400, detail="Invalid file format. Only JPG and PNG are allowed.")
        # Save the uploaded image prefer S3 for file storing and deleting
        img_filename = f"{ObjectId()}.{img.filename.rsplit('.', 1)[1].lower()}"
        img_path = os.path.join("uploads", img_filename)
        await save_image(img, img_path)

        
        movie_data = jsonable_encoder(movie)
        movie_data['img'] = img_path
        
        new_movie = await movie_collection.insert_one(movie_data)
        logger.info(f"Inserted Movie ID: {new_movie.inserted_id}")
        created_movie = await movie_collection.find_one({"_id": new_movie.inserted_id})
        return movie_helper(created_movie)
    except Exception as e:
        logger.error(f"Error occurred while creating the movie: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while creating the movie. Error: {e}")



@routs.get("/get_all_movies/", response_model=List[GetMovie])
async def get_movies():
    try:
        movies = []
        async for movie in movie_collection.find():
            movies.append(movie_helper(movie))

        logger.info(f"Retrieved {len(movies)} movies")
        return movies

    except Exception as e:
        logger.error(f"Error occurred while retrieving movies: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving movies.")
    


@routs.get("/get_movies/{id}", response_model=GetMovie)
async def get_movie(id: str):
    try:
        movie = await movie_collection.find_one({"_id": ObjectId(id)})
        if movie:
            logger.info(f"Retrieved movie with ID: {id}")
            return movie_helper(movie)
        raise HTTPException(status_code=404, detail="Movie not found")
    
    except Exception as e:
        logger.error(f"Error occurred while retrieving the movie with ID {id}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the movie.")

@routs.put("/update_movies/{id}", response_model=Movie)
async def update_movie(id: str,movie_name,movie_summary,img: UploadFile = None):
    try:
        movie_data = {
                "name": movie_name,
                "summary": movie_summary
                 }

        # Handle image file if provided
        if img:
            if not is_allowed_file(img.filename):
                raise HTTPException(status_code=400, detail="Invalid file format. Only JPG and PNG are allowed.")
            
            existing_movie = await movie_collection.find_one({"_id": ObjectId(id)})
            img_path = existing_movie.get('img')

            #removing prvious file from system 
            
            if img_path and os.path.exists(img_path):
                os.remove(img_path)
            img_filename = f"{ObjectId()}.{img.filename.rsplit('.', 1)[1].lower()}"
            img_path = os.path.join("uploads", img_filename)
            await save_image(img, img_path)
            movie_data['img'] = img_path
        
        movie_data = {k: v for k, v in movie_data.items() if v is not None}
        update_result = await movie_collection.update_one({"_id": ObjectId(id)}, {"$set": movie_data})
        
        if update_result.modified_count == 1:
            updated_movie = await movie_collection.find_one({"_id": ObjectId(id)})
            if updated_movie:
                logger.info(f"Updated movie with ID: {id}")
                return movie_helper(updated_movie)

        if existing_movie:
            logger.info(f"No changes made to the movie with ID: {id}")
            return movie_helper(existing_movie)

        raise HTTPException(status_code=404, detail="Movie not found")
    except Exception as e:
        logger.error(f"Error occurred while updating the movie with ID {id}: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while updating the movie. Error: {e}")

@routs.delete("/delete_movies/{id}")
async def delete_movie(id: str):
    try:
        movie = await movie_collection.find_one({"_id": ObjectId(id)})
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        delete_result = await movie_collection.delete_one({"_id": ObjectId(id)})
        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Movie not found")

        img_path = movie.get('img')
        if img_path and os.path.exists(img_path):
            os.remove(img_path)
        
        return {"status": "Movie deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while deleting the movie. Error: {e}")






