from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from . import models, schemas
from .models import Usuario


# 🟢 Crear una sola denuncia
def create_denuncia(db: Session, denuncia: schemas.DenunciaCreate):
    db_denuncia = models.Denuncia(**denuncia.model_dump())
    db.add(db_denuncia)
    db.commit()
    db.refresh(db_denuncia)
    return db_denuncia


# 🟢 Crear múltiples denuncias (carga masiva)
def create_denuncias_bulk(db: Session, denuncias: List[schemas.DenunciaCreate]):
    objs = [models.Denuncia(**d.model_dump()) for d in denuncias]
    db.add_all(objs)
    db.commit()
    return len(objs)


# 🟢 Obtener denuncias (para API o paginación)
def get_denuncias(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Denuncia)
        .order_by(models.Denuncia.creado_en.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# 🟢 Listar denuncias (para plantillas o dashboard)
def listar_denuncias(db: Session, limit: int = 1000):
    return (
        db.query(models.Denuncia)
        .order_by(models.Denuncia.id.desc())
        .limit(limit)
        .all()
    )


# 🟢 Cantidad total de denuncias
def get_denuncia_count(db: Session):
    return db.query(models.Denuncia).count()


# 🟢 Agrupar por distrito
def get_denuncias_por_distrito(db: Session):
    return dict(
        db.query(models.Denuncia.distrito, func.count(models.Denuncia.id))
        .group_by(models.Denuncia.distrito)
        .all()
    )


# 🟢 Agrupar por tipo de denuncia
def get_tipos_denuncia(db: Session):
    return dict(
        db.query(models.Denuncia.tipo_denuncia, func.count(models.Denuncia.id))
        .group_by(models.Denuncia.tipo_denuncia)
        .all()
    )


# 🟢 Obtener estadísticas generales del dashboard
def get_dashboard_stats(db: Session):
    total = get_denuncia_count(db)
    por_distrito = get_denuncias_por_distrito(db)
    tipos = get_tipos_denuncia(db)

    return schemas.DashboardStats(
        total_denuncias=total,
        denuncias_por_distrito=por_distrito,
        tipos_denuncia=tipos,
    )


# 🟢 Buscar usuario por correo electrónico
def get_user_by_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()

def get_direcciones_para_mapa(db: Session, zona: str = None, tipo: str = None, turno: str = None):
    """
    Devuelve las direcciones (direccion_ocurrencia) filtradas según zona, tipo y turno.
    """
    query = db.query(models.Denuncia)

    if zona:
        query = query.filter(models.Denuncia.distrito == zona)

    if tipo:
        query = query.filter(models.Denuncia.tipo_denuncia == tipo)

    # Turno día = entre 6 y 18 horas, noche = resto
    if turno == "día":
        query = query.filter(func.strftime('%H', models.Denuncia.hora_hecho).cast(Integer).between(6, 18))
    elif turno == "noche":
        query = query.filter(
            (func.strftime('%H', models.Denuncia.hora_hecho).cast(Integer) < 6) |
            (func.strftime('%H', models.Denuncia.hora_hecho).cast(Integer) > 18)
        )

    return query.all()
from sqlalchemy import extract

def get_direcciones_para_mapa(db: Session, zona: str = None, tipo: str = None, turno: str = None):
    """
    Devuelve las denuncias filtradas por zona, tipo y turno, con lat/lon.
    """
    query = db.query(models.Denuncia)

    if zona:
        query = query.filter(models.Denuncia.zona == zona)  # Asegúrate de usar la columna correcta

    if tipo:
        query = query.filter(models.Denuncia.tipo_denuncia == tipo)

    if turno == "día":
        query = query.filter(extract('hour', models.Denuncia.hora_hecho).between(6, 17))
    elif turno == "noche":
        query = query.filter(
            (extract('hour', models.Denuncia.hora_hecho) >= 18) |
            (extract('hour', models.Denuncia.hora_hecho) < 6)
        )

    return query.all()
