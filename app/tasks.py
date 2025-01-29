from celery import Celery
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models
import openai

celery_app = Celery('tasks', broker='redis://default:bS7wTdkZR7XtTrPfqtF6RO7cPsjeqZL6@redis-15809.c305.ap-south-1-1.ec2.redns.redis-cloud.com:15809')

@celery_app.task
def log_access(text: str):
    db = SessionLocal()
    try:
        log = models.AccessLog(text=text)
        db.add(log)
        db.commit()
    finally:
        db.close()

@celery_app.task
def analyze_review_sentiment(review_id: int):
    db = SessionLocal()
    try:
        review = db.query(models.ReviewHistory).filter(models.ReviewHistory.id == review_id).first()
        if review and (review.tone is None or review.sentiment is None):
            # Use OpenAI API to analyze sentiment and tone
            openai.api_key = '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'
            response = openai.Completion.create(
                engine="text-davinci-002",  
                prompt=f"Analyze the tone and sentiment of this review:\n\nText: {review.text}\nStars: {review.stars}\n\nTone:",
                max_tokens=60
            )
            tone = response.choices[0].text.strip()

            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=f"Analyze the tone and sentiment of this review:\n\nText: {review.text}\nStars: {review.stars}\n\nSentiment:",
                max_tokens=60
            )
            sentiment = response.choices[0].text.strip()

            review.tone = tone
            review.sentiment = sentiment
            db.commit()
    finally:
        db.close()
