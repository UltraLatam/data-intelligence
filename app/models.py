from sqlalchemy import Column, Integer, String, Date, Time, Text, TIMESTAMP, func
from .database import Base

class Denuncia(Base):
    __tablename__ = "denuncias"

    id = Column(Integer, primary_key=True, index=True)

    # Estos nombres de atributo quedan como los usa tu app/plantillas:
    fecha_registro = Column(Date, nullable=False)
    hora_registro  = Column(Time, nullable=False)
    comisaria      = Column("nombre_comisaria", String(120), nullable=False)
    efectivo       = Column("efectivo_policial", String(120), nullable=False)
    denunciante    = Column("nombre_denunciante", String(150), nullable=False)
    distrito       = Column(String(120), nullable=False)

    # Campos extra que sí existen en tu tabla
    hora_hecho     = Column(Time, nullable=True)
    tipo_denuncia  = Column(String(120), nullable=True)

    observaciones  = Column(Text)
    creado_en      = Column("fecha_creacion", TIMESTAMP, server_default=func.now())
