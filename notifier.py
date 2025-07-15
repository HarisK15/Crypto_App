import os
from dotenv import load_dotenv
import smtplib
from smtplib import SMTP
from email.message import EmailMessage


load_dotenv()
email = os.getenv("GOOGLE_ACC")
password = os.getenv("GOOGLE_PASS")
acc_email = os.getenv("EMAIL_ADDRESS")

def send_email_alert(recipient, subject, body):
    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()
        connection.login(email, password)
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = acc_email
        msg['To'] = recipient
        msg.set_content(body)
        connection.send_message(msg)


