from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse  
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, get_db
from .routers import denuncias
from . import models, crud
import os

# Crear las tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Denuncias Ciudadanas", version="1.0.0")

# Configurar archivos estáticos y templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Incluir routers
app.include_router(denuncias.router, prefix="/api/denuncias", tags=["denuncias"])

# Rutas para páginas HTML
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    stats = crud.get_dashboard_stats(db)
    return templates.TemplateResponse(
        "dashboard.html", 
        {"request": request, "stats": stats}
    )

@app.get("/carga-denuncias", response_class=HTMLResponse)
async def carga_denuncias(request: Request):
    return templates.TemplateResponse(
        "carga_denuncias.html", 
        {"request": request}
    )

@app.get("/listado-denuncias")
async def listado_denuncias(request: Request, db: Session = Depends(get_db)):
    denuncias = crud.get_denuncias(db, limit=1000)

    # Serializar a dicts simples para el JS del template
    def s(d):
        return {
            "id": d.id,
            "fecha_registro": d.fecha_registro.isoformat() if d.fecha_registro else None,
            "hora_registro": d.hora_registro.isoformat() if d.hora_registro else None,
            "comisaria": d.comisaria,
            "efectivo": d.efectivo,
            "denunciante": d.denunciante,
            "distrito": d.distrito,
            "hora_hecho": d.hora_hecho.isoformat() if d.hora_hecho else None,
            "tipo_denuncia": d.tipo_denuncia,
            "observaciones": d.observaciones or "",
        }

    denuncias_json = [s(x) for x in denuncias]

    return templates.TemplateResponse(
        "listado_denuncias.html",
        {
            "request": request,
            "denuncias": denuncias,           # para las filas renderizadas por Jinja
            "denuncias_json": denuncias_json  # para el JS (filtros/paginación)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)