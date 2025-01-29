from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import engine, get_db
from .tasks import log_access, analyze_review_sentiment

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/reviews/trends", response_model=list[schemas.CategoryTrend])
def get_review_trends(db: Session = Depends(get_db)):
    log_access.delay("GET /reviews/trends")
    return crud.get_top_categories(db)

@app.get("/reviews/", response_model=schemas.ReviewsResponse)
def get_reviews(
    category_id: int = Query(...),
    cursor: str = Query(None),
    db: Session = Depends(get_db)
):
    log_access.delay(f"GET /reviews/?category_id={category_id}")
    reviews_response = crud.get_reviews_by_category(db, category_id, cursor)
    for review in reviews_response.reviews:
        if review.tone is None or review.sentiment is None:
            analyze_review_sentiment.delay(review.id)
    
    return reviews_response
