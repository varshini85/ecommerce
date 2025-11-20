import os
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
import logging
from typing import Dict, Any

from model.subscription import Subscription
from utils.send_mail import send_email
from service.subscription_temp import welcome_email_template, admin_alert_template

logger = logging.getLogger(__name__)

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

BRAND_NAME = "Ecommerce Store"

def subscription(*, db: Session, payload) -> Dict[str, Any]:
    try:
        email_norm = payload.email.strip().lower()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid email")

    try:
        existing = (
            db.query(Subscription)
            .filter(func.lower(Subscription.email) == email_norm)
            .first()
        )
    except Exception:
        logger.exception("DB error while querying subscription table")
        raise HTTPException(status_code=500, detail="DB error")

    if not existing:
        try:
            new = Subscription(
                email=email_norm,
                subscribed=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            db.add(new)
            db.commit()
            db.refresh(new)

            subject_user = f"Welcome to {BRAND_NAME} — Thanks for subscribing!"
            html_user = welcome_email_template(
                brand_name=BRAND_NAME
            )
            send_email(
                to_email_id=new.email,
                subject=subject_user,
                content_to_be_sent=html_user
            )

            subject_admin = f"New Subscriber: {new.email}"
            html_admin = admin_alert_template(
                brand_name=BRAND_NAME,
                subscriber_email=new.email
            )
            send_email(
                to_email_id=ADMIN_EMAIL,
                subject=subject_admin,
                content_to_be_sent=html_admin
            )

            return {"message": "Subscribed"}

        except HTTPException:
            raise

        except Exception:
            logger.exception("Failed to create subscriber or send email")
            try:
                db.rollback()
            except Exception:
                pass
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to subscribe",
            )

    return {"message": "Already subscribed"}
