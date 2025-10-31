# app/schemas.py
from pydantic import BaseModel
from datetime import date, time, datetime
from typing import Optional, Dict

# Usamos los nombres que consume la app/plantillas:
#  - comisaria  -> columna "nombre_comisaria" (mapeada en models.py)
#  - efectivo   -> columna "efectivo_policial"
#  - denunciante-> columna "nombre_denunciante"
#  - creado_en  -> columna "fecha_creacion"

class DenunciaBase(BaseModel):
    fecha_registro: date
    hora_registro: time
    comisaria: str
    efectivo: str
    denunciante: str
    distrito: str
    hora_hecho: Optional[time] = None
    tipo_denuncia: Optional[str] = None
    observaciones: Optional[str] = None
    direccion_ocurrencia: Optional[str] = None

class DenunciaCreate(DenunciaBase):
    pass

class DenunciaResponse(DenunciaBase):
    id: int
    creado_en: datetime   # <- coincide con el atributo del modelo
    class Config:
        from_attributes = True

# (Opcional) alias si en alguna parte esperas "DenunciaOut"
class DenunciaOut(DenunciaResponse):
    pass

class DashboardStats(BaseModel):
    total_denuncias: int
    denuncias_por_distrito: Dict[str, int]
    tipos_denuncia: Dict[str, int]
