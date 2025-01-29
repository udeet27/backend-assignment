from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from . import models, schemas
from typing import List

def get_top_categories(db: Session, limit: int = 5) -> List[schemas.CategoryTrend]:
    subquery = db.query(
        models.ReviewHistory.category_id,
        models.ReviewHistory.review_id,
        func.max(models.ReviewHistory.created_at).label("max_created_at")
    ).group_by(models.ReviewHistory.category_id, models.ReviewHistory.review_id).subquery()

    result = db.query(
        models.Category.id,
        models.Category.name,
        models.Category.description,
        func.avg(models.ReviewHistory.stars).label("average_stars"),
        func.count(models.ReviewHistory.id).label("total_reviews")
    ).join(subquery, models.Category.id == subquery.c.category_id
    ).join(models.ReviewHistory, (models.ReviewHistory.category_id == subquery.c.category_id) &
                                 (models.ReviewHistory.review_id == subquery.c.review_id) &
                                 (models.ReviewHistory.created_at == subquery.c.max_created_at)
    ).group_by(models.Category.id
    ).order_by(desc("average_stars")
    ).limit(limit).all()

    return [schemas.CategoryTrend(
        id=r.id,
        name=r.name,
        description=r.description,
        average_stars=float(r.average_stars),
        total_reviews=r.total_reviews
    ) for r in result]

def get_reviews_by_category(db: Session, category_id: int, cursor: str, limit: int = 15) -> List[schemas.Review]:
    query = db.query(models.ReviewHistory).filter(models.ReviewHistory.category_id == category_id)

    if cursor:
        query = query.filter(models.ReviewHistory.created_at < cursor)

    result = query.order_by(desc(models.ReviewHistory.created_at)).limit(limit + 1).all()

    next_cursor = None
    if len(result) > limit:
        next_cursor = result[-1].created_at.isoformat()
        result = result[:limit]

    reviews = [schemas.Review(
        id=r.id,
        text=r.text,
        stars=r.stars,
        review_id=r.review_id,
        created_at=r.created_at.isoformat(),
        tone=r.tone,
        sentiment=r.sentiment,
        category_id=r.category_id
    ) for r in result]

    return schemas.ReviewsResponse(reviews=reviews, next_cursor=next_cursor)
