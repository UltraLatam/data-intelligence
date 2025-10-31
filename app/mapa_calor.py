# crear_mapa.py - POSTGRESQL + MAPA DE CALOR EN COLOR
import pandas as pd
import time
from geopy.geocoders import Nominatim
import folium
from folium.plugins import HeatMap
import os

# === CONFIGURACIÓN DE POSTGRESQL (¡CAMBIAR ESTO!) ===
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',           # Cambia por tu usuario
    'password': 'admin',         # Cambia por tu contraseña
    'database': 'incidentes_db',    # Cambia por tu base de datos
    'tabla': 'direcciones'        # Cambia por tu tabla
}

print("Conectando a PostgreSQL...")

# === 1. CONECTAR A POSTGRESQL Y CARGAR DATOS ===
try:
    import psycopg2
    conn_str = (
        f"host={DB_CONFIG['host']} "
        f"port={DB_CONFIG['port']} "
        f"user={DB_CONFIG['user']} "
        f"password={DB_CONFIG['password']} "
        f"dbname={DB_CONFIG['database']}"
    )
    conn = psycopg2.connect(conn_str)
    query = f"SELECT rua, cidade, estado, pais FROM {DB_CONFIG['tabla']}"
    df = pd.read_sql(query, conn)
    conn.close()
    print(f"¡Conectado! {len(df)} direcciones cargadas desde PostgreSQL.")
except ImportError:
    print("ERROR: Instala psycopg2: pip install psycopg2-binary")
    exit()
except Exception as e:
    print(f"ERROR de conexión: {e}")
    print("Verifica: host, port, user, password, database y tabla.")
    exit()

# Validar columnas
required = ['rua', 'cidade', 'estado', 'pais']
missing = [col for col in required if col not in df.columns]
if missing:
    print(f"ADVERTENCIA: Faltan columnas: {missing}")
    print("Ajusta el SELECT en el query.")
    exit()

# === 2. GEOCODIFICAR ===
geolocator = Nominatim(user_agent="HeatMap_PostgreSQL_Bustamante")
geocodes = []

print("Geocodificando direcciones desde PostgreSQL...")
for i, row in df.iterrows():
    addr = f"{row['rua']}, {row['cidade']}, {row['estado']}, {row['pais']}"
    try:
        location = geolocator.geocode(addr, timeout=10)
        if location:
            geocodes.append([location.latitude, location.longitude])
            print(f"OK {i+1}/{len(df)}")
        else:
            print(f"NO {i+1}/{len(df)}")
    except Exception as e:
        print(f"ERROR: {e}")
    time.sleep(1.1)

# === 3. DATAFRAME + FILTRO DISTRITO ===
dfa = pd.DataFrame(geocodes, columns=['lat', 'lng'])

# Bounding box del distrito
lat_min, lat_max = -16.43, -16.35
lng_min, lng_max = -71.56, -71.49

mask = (dfa['lat'].between(lat_min, lat_max)) & (dfa['lng'].between(lng_min, lng_max))
dfa_distrito = dfa[mask]

print(f"\nPuntos en el distrito: {len(dfa_distrito)} / {len(dfa)}")

if len(dfa_distrito) == 0:
    print("Usando todos los puntos.")
    dfa_distrito = dfa

# === 4. MAPA EN COLOR ===
m = folium.Map(
    location=[-16.385, -71.525],
    zoom_start=13,
    tiles='OpenStreetMap'
)

# === 5. HEATMAP ===
HeatMap(
    data=dfa_distrito[['lat', 'lng']].values.tolist(),
    radius=25,
    blur=20,
    min_opacity=0.4,
    gradient={0.0: 'navy', 0.3: 'blue', 0.5: 'lime', 0.7: 'yellow', 1.0: 'red'}
).add_to(m)

# === 6. TÍTULO CON DATOS DE BD ===
total_bd = len(df)
total_mapa = len(dfa_distrito)
titulo_html = f'''
<h3 align="center" style="font-size:20px; font-weight:bold; color:#d35400; margin:15px;">
Mapa de Calor desde PostgreSQL
</h3>
<p align="center" style="font-size:14px; color:#2c3e50;">
{total_bd} direcciones en BD → {total_mapa} puntos en el mapa
</p>
'''
m.get_root().html.add_child(folium.Element(titulo_html))

# === 7. MARCADOR CENTRAL ===
folium.Marker(
    location=[-16.385, -71.525],
    popup="José Luis Bustamante y Rivero",
    icon=folium.Icon(color='red', icon='info-sign')
).add_to(m)

# === 8. GUARDAR ===
os.makedirs("results", exist_ok=True)
output_file = "results/Heatmap.html"
m.save(output_file)

print(f"\n¡MAPA DE CALOR GENERADO DESDE POSTGRESQL!")
print(f"Archivo: {output_file}")
print("Abre en tu navegador.")