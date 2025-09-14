from fastapi import FastAPI, Form
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FastAPI Gmail Contact Mailer")

# Enable CORS so your frontend can call the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.vercel.app"],  # replace "*" with your frontend domain for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gmail credentials from environment variables
CLIENT_ID = os.environ["GMAIL_CLIENT_ID"]
CLIENT_SECRET = os.environ["GMAIL_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["GMAIL_REFRESH_TOKEN"]
USER_EMAIL = os.environ["GMAIL_USER_EMAIL"]

creds = Credentials(
    token=None,
    refresh_token=REFRESH_TOKEN,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    token_uri="https://oauth2.googleapis.com/token",
    scopes=["https://www.googleapis.com/auth/gmail.send"]
)

service = build("gmail", "v1", credentials=creds)

def send_email(to_email: str, from_email: str, subject: str, body_text: str):
    email_message = MIMEText(body_text)
    email_message["to"] = to_email
    email_message["from"] = from_email
    email_message["subject"] = subject
    raw = base64.urlsafe_b64encode(email_message.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()

@app.post("/send-mail/")
def send_mail(name: str = Form(...), email: str = Form(...), message: str = Form(...)):
    admin_body = f"Name: {name}\nEmail: {email}\nMessage:\n{message}"
    send_email(USER_EMAIL, USER_EMAIL, f"New Contact Form from {name}", admin_body)

    user_body = (
        f"Hi {name},\n\nThank you for reaching out! "
        "We received your message and will contact you soon.\n\nBest regards,\nARMS Tech Innovations"
    )
    send_email(email, USER_EMAIL, "We Received Your Message", user_body)

    return {"status": "Emails sent successfully!"}
