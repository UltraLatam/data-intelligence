# app/auth.py
from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer
from fastapi import HTTPException
import smtplib
from email.mime.text import MIMEText
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "clave_secreta_123")
APP_HOST = os.getenv("APP_HOST", "http://127.0.0.1:8000")

serializer = URLSafeTimedSerializer(SECRET_KEY)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

def generate_reset_token(email: str):
    return serializer.dumps(email, salt="password-reset")

def verify_reset_token(token: str, expiration=3600):
    try:
        return serializer.loads(token, salt="password-reset", max_age=expiration)
    except Exception:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")

def send_reset_email(to_email: str, token: str):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    mail_from = os.getenv("MAIL_FROM", smtp_user)

    reset_url = f"{APP_HOST}/reset-password?token={token}"

    message = MIMEText(f"""
    Hola,<br><br>
    Has solicitado restablecer tu contraseña.<br>
    <a href="{reset_url}">Haz clic aquí</a> para restablecerla.
    """, "html")
    message["Subject"] = "Recuperación de contraseña"
    message["From"] = mail_from
    message["To"] = to_email

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(mail_from, to_email, message.as_string())
