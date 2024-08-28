import logging
from typing import List, Optional
from fastapi import APIRouter, File, HTTPException, UploadFile, Form
from pydantic import HttpUrl
from schemas import GetMovie, Movie
from fastapi.encoders import jsonable_encoder
from database.dbconnection import movie_collection, grid_fs
from bson import ObjectId
from common import is_allowed_file, movie_helper
import bson
import os

routs = APIRouter()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)



@routs.post("/movies/", response_model=Movie)
async def create_movie(movie_name: str, movie_summary: Optional[str] = None, img: UploadFile = File(...)):
    try:
        movie = {
            "name": movie_name,
            "summary": movie_summary
        }

        if not is_allowed_file(img.filename):
            raise HTTPException(status_code=400, detail="Invalid file format. Only JPG and PNG are allowed.")

        # Save the uploaded image to GridFS
        file_id = await grid_fs.upload_from_stream(img.filename, img.file, metadata={"content_type": img.content_type})
        movie_data = jsonable_encoder(movie)
        movie_data['img'] = {"file_id": str(file_id), "filename": img.filename, "content_type": img.content_type}

    
        new_movie = await movie_collection.insert_one(movie_data)
        logger.info(f"Inserted Movie ID: {new_movie.inserted_id}")
        created_movie = await movie_collection.find_one({"_id": new_movie.inserted_id})
        return movie_helper(created_movie)
    
    except HTTPException as http_exc:
        logger.error(f"HTTP Exception occurred: {http_exc.detail}")
        raise http_exc
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
    
    except HTTPException as http_exc:
        logger.error(f"HTTP Exception occurred: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while retrieving the movie with ID {id}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the movie.")



@routs.put("/update_movies/{id}", response_model=Movie)
async def update_movie(id: str, movie_name: str, movie_summary: Optional[str] = None, img: UploadFile = None):
    try:
        movie_data = {
            "name": movie_name,
            "summary": movie_summary
        }

        if img:
            if not is_allowed_file(img.filename):
                raise HTTPException(status_code=400, detail="Invalid file format. Only JPG and PNG are allowed.")

            existing_movie = await movie_collection.find_one({"_id": ObjectId(id)})
            if not existing_movie:
                raise HTTPException(status_code=404, detail="Movie not found")

            # Delete the old image from GridFS
            old_img_metadata = existing_movie.get('img')
            if old_img_metadata and old_img_metadata.get("file_id"):
                await grid_fs.delete(ObjectId(old_img_metadata["file_id"]))

            # Save the new image to GridFS
            file_id = await grid_fs.upload_from_stream(img.filename, img.file, metadata={"content_type": img.content_type})
            movie_data['img'] = {"file_id": str(file_id), "filename": img.filename, "content_type": img.content_type}

        movie_data = {k: v for k, v in movie_data.items() if v is not None}
        update_result = await movie_collection.update_one({"_id": ObjectId(id)}, {"$set": movie_data})

        if update_result.modified_count == 1:
            updated_movie = await movie_collection.find_one({"_id": ObjectId(id)})
            if updated_movie:
                logger.info(f"Updated movie with ID: {id}")
                return movie_helper(updated_movie)
        raise HTTPException(status_code=404, detail="Movie not found")
    
    except HTTPException as http_exc:
        logger.error(f"HTTP Exception occurred: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while updating the movie with ID {id}: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while updating the movie. Error: {e}")






@routs.delete("/delete_movies/{id}")
async def delete_movie(id: str):
    try:
        object_id = ObjectId(id)
        
        movie = await movie_collection.find_one({"_id": ObjectId(id)})
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        # Delete the associated image from GridFS if it exists
        img_metadata = movie.get('img')
        if img_metadata and img_metadata.get("file_id"):
            file_id = ObjectId(img_metadata["file_id"])
            logger.info(f"Deleting file with ID: {file_id}")
            try:
                await grid_fs.delete(file_id)
                logger.info(f"File with ID {file_id} deleted from GridFS.")
            except Exception as e:
                logger.error(f"Error occurred while deleting file from GridFS: {e}")
                raise HTTPException(status_code=500, detail="Error deleting file from GridFS")

        # Delete the movie document from the collection
        delete_result = await movie_collection.delete_one({"_id": object_id})
        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Movie not found during deletion")

        logger.info(f"Movie with ID {id} deleted from collection.")
        return {"status": "Movie deleted"}
    
    except HTTPException as http_exc:
        logger.error(f"HTTP Exception occurred: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred while deleting the movie with ID {id}: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while deleting the movie. Error: {e}")
