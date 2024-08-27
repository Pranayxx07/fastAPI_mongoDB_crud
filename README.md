# FastAPI Movie Database API

This project is a RESTful API built with FastAPI and MongoDB for managing a movie database. The API allows you to create, retrieve, update, and delete movie records. 

## Features

- **Create a Movie**: Add new movies to the database.
- **Retrieve Movies**: Fetch all movies or get details of a specific movie by its ID.
- **Update a Movie**: Modify movie details by ID.
- **Delete a Movie**: Remove a movie from the database by ID.
- **Logging**: Integrated logging for monitoring and debugging.

## Getting Started

### Prerequisites

- **Python 3.8+**: Make sure you have Python installed.
- **MongoDB**: Ensure you have access to a MongoDB instance.

### Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/Pranayxx07/fastAPI_mongoDB_crud.git
    cd fastAPI_mongoDB_crud
    ```

2. **Create a virtual environment**:
    ```bash
    python3 -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. **Install the dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure MongoDB Connection**:
   - Update the MongoDB connection details in `database/dbconnection.py` to point to your MongoDB instance.

### Running the API

Start the FastAPI server:

```bash
uvicorn main:app --reload --port 8000
