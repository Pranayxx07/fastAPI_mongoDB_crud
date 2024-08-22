def movie_helper(movie) -> dict:
    return {
        "id": str(movie["_id"]),
        "name": movie["name"],
        "img": movie["img"],
        "summary": movie["summary"],
    }
