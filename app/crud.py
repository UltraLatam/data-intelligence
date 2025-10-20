from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas
from typing import List

def create_denuncia(db: Session, denuncia: schemas.DenunciaCreate):
    db_denuncia = models.Denuncia(**denuncia.model_dump())
    db.add(db_denuncia)
    db.commit()
    db.refresh(db_denuncia)
    return db_denuncia

def create_denuncias_bulk(db: Session, denuncias: List[schemas.DenunciaCreate]):
    objs = [models.Denuncia(**d.model_dump()) for d in denuncias]
    db.add_all(objs)
    db.commit()
    return len(objs)

def get_denuncias(db: Session, skip: int = 0, limit: int = 100):
    # OJO: ahora el campo es creado_en (antes usabas fecha_creacion)
    return (
        db.query(models.Denuncia)
        .order_by(models.Denuncia.creado_en.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

# Para la vista/plantilla conviene devolver ORM puro:
def listar_denuncias(db: Session, limit: int = 1000):
    return (
        db.query(models.Denuncia)
        .order_by(models.Denuncia.id.desc())
        .limit(limit)
        .all()
    )

def get_denuncia_count(db: Session):
    return db.query(models.Denuncia).count()

def get_denuncias_por_distrito(db: Session):
    return dict(
        db.query(models.Denuncia.distrito, func.count(models.Denuncia.id))
        .group_by(models.Denuncia.distrito)
        .all()
    )

def get_tipos_denuncia(db: Session):
    return dict(
        db.query(models.Denuncia.tipo_denuncia, func.count(models.Denuncia.id))
        .group_by(models.Denuncia.tipo_denuncia)
        .all()
    )

def get_dashboard_stats(db: Session):
    total = get_denuncia_count(db)
    por_distrito = get_denuncias_por_distrito(db)
    tipos = get_tipos_denuncia(db)
    return schemas.DashboardStats(
        total_denuncias=total,
        denuncias_por_distrito=por_distrito,
        tipos_denuncia=tipos,
    )
