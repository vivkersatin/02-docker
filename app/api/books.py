from typing import List
from fastapi import APIRouter, HTTPException, status
from tortoise.exceptions import DoesNotExist

from .models import Book
from .schemas import BookIn_Pydantic, BookOut_Pydantic

router = APIRouter()

# --- API endpoints for books (for a RESTful API client) ---
@router.get("/api/books", response_model=List[BookOut_Pydantic], tags=["Books API"])
async def get_all_books_api():
    return await Book.all()

@router.post("/api/books", response_model=BookOut_Pydantic, status_code=201, tags=["Books API"])
async def create_book_api(book_in: BookIn_Pydantic):
    return await Book.create(**book_in.model_dump())

@router.get("/api/books/{book_id}", response_model=BookOut_Pydantic, tags=["Books API"])
async def get_book_api(book_id: int):
    try: return await Book.get(id=book_id)
    except DoesNotExist: raise HTTPException(status_code=404, detail="Book not found")

@router.put("/api/books/{book_id}", response_model=BookOut_Pydantic, tags=["Books API"])
async def update_book_api(book_id: int, book_in: BookIn_Pydantic):
    try: book = await Book.get(id=book_id); await book.update_from_dict(book_in.model_dump()).save(); return book
    except DoesNotExist: raise HTTPException(status_code=404, detail="Book not found")

@router.delete("/api/books/{book_id}", status_code=204, tags=["Books API"])
async def delete_book_api(book_id: int):
    try: await (await Book.get(id=book_id)).delete()
    except DoesNotExist: raise HTTPException(status_code=404, detail="Book not found")
