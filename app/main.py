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






@app.get("/prediccion-ia", response_class=HTMLResponse)
def prediccion_ia_page(request: Request, db: Session = Depends(get_db)):
    """
    Vista estática inicial de la sección 'Predicción IA'.
    Por ahora solo muestra la página y más adelante le metemos la lógica de riesgo por zona/turno.
    """
    # Si más adelante quieres traer datos reales (ej: zonas existentes, tipos de denuncia),
    # acá los consultas con crud y los mandas al template.
    zonas_disponibles = ["Zona 1", "Zona 2", "Zona 3", "Zona 4", "Zona 5", "Zona 6", "Zona 7"]

    return templates.TemplateResponse(
        "prediccion-ia.html",
        {
            "request": request,
            "zonas": zonas_disponibles
        }
    )





@app.get("/zonas", response_class=HTMLResponse)
def zonas_page(request: Request, db: Session = Depends(get_db)):
    """
    Vista informativa / analítica de Zonas.
    Más adelante aquí podemos mostrar:
    - mapa por zona
    - conteo de denuncias por zona
    - nivel de riesgo histórico por zona
    """
    # Ejemplo: podemos calcular denuncias por "zona" desde la BD.
    # Ahora mismo tu campo en BD se llama 'distrito' pero lo están usando como 'Zona 1', 'Zona 2', etc.
    # Vamos a mandar ese resumen al template.
    zonas_stats = crud.get_denuncias_por_distrito(db)
    # zonas_stats es algo tipo {"Zona 1": 12, "Zona 2": 9, ...}

    return templates.TemplateResponse(
        "zonas.html",
        {
            "request": request,
            "zonas_stats": zonas_stats
        }
    )


@app.get("/horarios", response_class=HTMLResponse)
def horarios_page(request: Request, db: Session = Depends(get_db)):
    """
    Vista para análisis por turno / franja horaria.
    Luego vamos a usar esto para justificar despliegue de patrullas en mañana/tarde/noche.
    """
    # Podemos ir construyendo stats de frecuencia por hora usando crud luego.
    # Por ahora mandamos una estructura mockeada para que la UI ya se pinte.
    horarios_stats = [
        {"label": "00:00 - 06:00", "denuncias": 5},
        {"label": "06:00 - 12:00", "denuncias": 11},
        {"label": "12:00 - 18:00", "denuncias": 18},
        {"label": "18:00 - 24:00", "denuncias": 14},
    ]

    return templates.TemplateResponse(
        "horarios.html",
        {
            "request": request,
            "horarios_stats": horarios_stats
        }
    )
