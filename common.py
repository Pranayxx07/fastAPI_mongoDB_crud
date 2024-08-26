from fastapi import UploadFile


def movie_helper(movie) -> dict:
    return {
        "id": str(movie["_id"]),
        "name": movie["name"],
        "img": movie["img"],
        "summary": movie["summary"],
    }


async def save_image(file: UploadFile, destination: str):
    with open(destination, "wb") as buffer:
        # Read the file content and write it to the new file
        content = await file.read()  # Read the file content asynchronously
        buffer.write(content) 


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS