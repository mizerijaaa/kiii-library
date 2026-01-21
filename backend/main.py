from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import time
import logging

# ------------------------
# App setup
# ------------------------
app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://grocery-app.local", "http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------
# MongoDB connection
# ------------------------
def get_mongo_uri():
    username = os.getenv("MONGO_INITDB_ROOT_USERNAME", "root")
    password = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "example")
    host = os.getenv("MONGO_HOST", "localhost")
    db = os.getenv("MONGO_DB", "books_db")
    return f"mongodb://{username}:{password}@{host}:27017/{db}?authSource=admin"

def connect_to_mongo(max_retries=5, retry_delay=5):
    uri = get_mongo_uri()
    logger.info(f"Connecting to MongoDB at {uri}")
    for attempt in range(max_retries):
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            client.server_info()
            logger.info("Connected to MongoDB")
            return client
        except Exception as e:
            logger.error(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise e

try:
    client = connect_to_mongo()
    db = client.books_db
    books_collection = db.books
except Exception as e:
    logger.error(f"MongoDB connection failed: {e}")
    raise

# ------------------------
# Pydantic model
# ------------------------
class Book(BaseModel):
    title: str
    author: str
    genre: str = "Unknown"
    year: int

# ------------------------
# Seed initial books
# ------------------------
@app.on_event("startup")
async def seed_data():
    if books_collection.count_documents({}) == 0:
        initial_books = [
            {"title": "1984", "author": "George Orwell", "genre": "Dystopian", "year": 1949},
            {"title": "The Hobbit", "author": "J.R.R. Tolkien", "genre": "Fantasy", "year": 1937},
            {"title": "Pride and Prejudice", "author": "Jane Austen", "genre": "Romance", "year": 1813},
        ]
        books_collection.insert_many(initial_books)
        logger.info("Seeded initial books")

# ------------------------
# API endpoints
# ------------------------
@app.get("/api/books")
async def get_books(title: str = None, author: str = None, genre: str = None):
    query = {}
    if title:
        query["title"] = {"$regex": title, "$options": "i"}
    if author:
        query["author"] = {"$regex": author, "$options": "i"}
    if genre:
        query["genre"] = {"$regex": genre, "$options": "i"}

    books = []
    for book in books_collection.find(query):
        book["_id"] = str(book["_id"])
        books.append(book)
    return books

@app.post("/api/books")
async def add_book(book: Book):
    result = books_collection.insert_one(book.dict())
    return {"id": str(result.inserted_id)}

@app.put("/api/books/{book_id}")
async def update_book(book_id: str, book: Book):
    result = books_collection.update_one({"_id": ObjectId(book_id)}, {"$set": book.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book updated"}

@app.delete("/api/books/{book_id}")
async def delete_book(book_id: str):
    result = books_collection.delete_one({"_id": ObjectId(book_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted"}

# ------------------------
# Run app
# ------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)