from sqlalchemy import Column, Integer, String, Date, Time, Text, TIMESTAMP, func
from .database import Base

class Denuncia(Base):
    __tablename__ = "denuncias"

    id = Column(Integer, primary_key=True, index=True)

    # Campos principales
    fecha_registro = Column(Date, nullable=False)
    hora_registro  = Column(Time, nullable=False)
    comisaria      = Column("nombre_comisaria", String(120), nullable=False)
    efectivo       = Column("efectivo_policial", String(120), nullable=False)
    denunciante    = Column("nombre_denunciante", String(150), nullable=False)
    distrito       = Column(String(120), nullable=False)

    # Campos adicionales existentes en la BD
    hora_hecho     = Column(Time, nullable=True)
    tipo_denuncia  = Column(String(120), nullable=True)
    observaciones  = Column(Text)

    # ✅ Campo nuevo agregado (ya existe en tu BD)
    direccion_ocurrencia = Column(String(255), nullable=True)

    # Fecha de creación
    creado_en = Column("fecha_creacion", TIMESTAMP, server_default=func.now())


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(50), default="analista")
    creado_en = Column(TIMESTAMP, server_default=func.now())
