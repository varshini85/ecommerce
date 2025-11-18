import smtplib
from email.message import EmailMessage
from fastapi import HTTPException
from dotenv import load_dotenv
import os

load_dotenv(override=True)

SMTP_HOST = os.getenv("SMTP_HOST")      # e.g. smtp.gmail.com
SMTP_PORT = int(os.getenv("SMTP_PORT")) # e.g. 587
SMTP_USER = os.getenv("SMTP_USER")      # your email
SMTP_PASS = os.getenv("SMTP_PASS")      # app password

def send_email(to_email_id, subject, content_to_be_sent):
    try:
        msg = EmailMessage()
        msg["From"] = SMTP_USER
        msg["To"] = to_email_id
        msg["Subject"] = subject
        msg.set_content(content_to_be_sent, subtype="html")

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()                     # secure connection
            server.login(SMTP_USER, SMTP_PASS)    # authenticate
            server.send_message(msg)

        return {"message": "Mail sent"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Not able to send email: {str(e)}")
