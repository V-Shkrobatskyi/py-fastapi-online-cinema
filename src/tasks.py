from datetime import datetime

from celery import Celery

from src.config.celery import celery_app
from src.database import ActivationToken
from src.database.database import SessionLocal

app = Celery("tasks", backend="redis://localhost", broker="redis://localhost")


@celery_app.task()
def delete_expired_activation_tokens():
    db = SessionLocal()
    try:
        expired_active_tokens = (
            db.query(ActivationToken)
            .filter(ActivationToken.expires_at < datetime.utcnow())
            .all()
        )
        for token in expired_active_tokens:
            db.delete(token)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error during expired token delete: {e}")
    finally:
        db.close()
