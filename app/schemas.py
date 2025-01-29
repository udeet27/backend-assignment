from pydantic import BaseModel
from typing import List

class CategoryTrend(BaseModel):
    id: int
    name: str
    description: str
    average_stars: float
    total_reviews: int

class Review(BaseModel):
    id: int
    text: str
    stars: int
    review_id: str
    created_at: str
    tone: str
    sentiment: str
    category_id: int

class ReviewsResponse(BaseModel):
    reviews: List[Review]
    next_cursor: str | None
