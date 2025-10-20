from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db
import pandas as pd
from datetime import datetime
from typing import List, Optional
import os
import math

router = APIRouter()

def _parse_time(value: Optional[str]):
    """
    Acepta 'HH:MM', objetos time, NaN/None -> devuelve time o None
    """
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    if hasattr(value, "hour") and hasattr(value, "minute"):
        # ya es datetime.time
        return value
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        return datetime.strptime(value, "%H:%M").time()
    return None

def _parse_date(value):
    """
    Acepta 'YYYY-MM-DD', objetos date/datetime, serial de Excel, NaN/None
    """
    if value is None or (isinstance(value, float) and math.isnan(value)):
        raise ValueError("fecha_registro es requerida")
    if hasattr(value, "year") and hasattr(value, "month") and hasattr(value, "day"):
        # date o datetime
        return value.date() if hasattr(value, "hour") else value
    if isinstance(value, str):
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    # Si viniera como número serial (Excel), que Pandas ya convierte normalmente
    # a datetime, pero por si acaso:
    try:
        return pd.to_datetime(value).date()
    except Exception:
        raise ValueError(f"Fecha inválida: {value}")

@router.post("/upload-excel/", response_model=dict)
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos Excel (.xlsx, .xls)")
    
    # Guardar archivo temporalmente
    upload_dir = "static/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    try:
        # Leer el archivo Excel
        df = pd.read_excel(file_path)

        # Validar columnas requeridas
        required_columns = [
            "fecha_registro", "hora_registro", "nombre_comisaria",
            "efectivo_policial", "nombre_denunciante", "distrito",
            "hora_hecho", "tipo_denuncia", "observaciones",
        ]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Columnas faltantes: {', '.join(missing_columns)}"
            )

        # Procesar y validar datos
        denuncias: List[schemas.DenunciaCreate] = []
        valid_distritos = ["Arequipa", "Cayma", "Cerro Colorado", "Paucarpata"]

        for index, row in df.iterrows():
            try:
                # Validar distrito
                distrito = str(row["distrito"]).strip()
                if distrito not in valid_distritos:
                    raise ValueError(f"Distrito inválido: {distrito}")

                fecha_registro = _parse_date(row["fecha_registro"])
                hora_registro = _parse_time(row["hora_registro"])
                hora_hecho    = _parse_time(row["hora_hecho"])

                denuncia = schemas.DenunciaCreate(
                    fecha_registro=fecha_registro,
                    hora_registro=hora_registro,
                    comisaria=str(row["nombre_comisaria"]).strip(),
                    efectivo=str(row["efectivo_policial"]).strip(),
                    denunciante=str(row["nombre_denunciante"]).strip(),
                    distrito=distrito,
                    hora_hecho=hora_hecho,
                    tipo_denuncia=(str(row["tipo_denuncia"]).strip()
                                   if pd.notna(row["tipo_denuncia"]) else None),
                    observaciones=(str(row["observaciones"]).strip()
                                   if pd.notna(row["observaciones"]) else None),
                )
                denuncias.append(denuncia)
            except Exception as e:
                # +2 porque el Excel tiene encabezado en la fila 1
                raise HTTPException(status_code=400, detail=f"Error en fila {index + 2}: {str(e)}")

        # Guardar en base de datos
        count = crud.create_denuncias_bulk(db, denuncias)

        # Eliminar archivo temporal
        os.remove(file_path)

        return {"message": f"Se cargaron {count} denuncias exitosamente", "denuncias_procesadas": count}

    except HTTPException:
        # Relevantar error tal cual
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")

@router.get("/", response_model=List[schemas.DenunciaResponse])
def get_denuncias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_denuncias(db, skip=skip, limit=limit)

@router.get("/stats/", response_model=schemas.DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    return crud.get_dashboard_stats(db)
