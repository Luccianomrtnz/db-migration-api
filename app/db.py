import json
import pyodbc
import os

# Obtener la ruta del archivo de configuración
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

# Cargar configuración desde el archivo JSON
with open(CONFIG_PATH) as f:
    config = json.load(f)  # Aquí está el error: faltaba cargar el JSON

# Establecer conexión con SQL Server
conn = pyodbc.connect(
    f'DRIVER={config["DRIVER"]};'
    f'SERVER={config["SERVER"]};'
    f'DATABASE={config["DATABASE"]};'
    f'UID={config["USER"]};'
    f'PWD={config["PASSWORD"]};'
    f'TrustServerCertificate={config["TrustServerCertificate"]};'
)

# Ejecutar consulta de prueba
cursor = conn.cursor()
cursor.execute("SELECT @@VERSION")
row = cursor.fetchone()
print("✅ Conexión exitosa a SQL Server:", row[0])