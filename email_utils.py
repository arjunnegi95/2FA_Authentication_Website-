import smtplib
from email.message import EmailMessage

EMAIL_ADDRESS = "arjunnegi352006@gmail.com"
EMAIL_PASSWORD = "jrsf qhxc yvfz kjsx"

def send_otp_email(to_email, otp):
    msg = EmailMessage()
    msg["Subject"] = "Your Login OTP"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg.set_content(
        f"Your OTP is {otp}\n\nThis OTP is valid for 5 minutes."
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)