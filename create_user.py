from app.database import SessionLocal
from app.models import Usuario
from app.auth import get_password_hash

db = SessionLocal()
user = Usuario(
    username="admin",
    email="admin@example.com",
    password_hash=get_password_hash("admin123"),
    rol="admin"
)
db.add(user)
db.commit()
print("✅ Usuario admin creado (admin / admin123)")
