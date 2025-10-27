import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# --- Cargar variables desde .env ---
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "denuncias_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "admin")

# --- Construcción segura de la URL ---
if DB_PASS:
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    # Si no hay contraseña, la omitimos para evitar error "no password supplied"
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- Motor de conexión y sesión ---
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Clase base para los modelos (SQLAlchemy 2.0) ---
class Base(DeclarativeBase):
    pass

# --- Dependencia para inyectar sesión en rutas ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Utilidad opcional para probar la conexión ---
def quick_test():
    """Imprime la versión de PostgreSQL para verificar la conexión."""
    try:
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version();")).scalar()
            print("✅ Conexión exitosa a PostgreSQL:")
            print(version)
    except Exception as e:
        print("❌ Error al conectar con la base de datos:")
        print(e)


# Si ejecutas este archivo directamente: prueba conexión
if __name__ == "__main__":
    quick_test()
