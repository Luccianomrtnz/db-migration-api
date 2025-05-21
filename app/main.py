from fastapi import FastAPI
from app.routes import router  # Importamos los endpoints de routes.py

# Inicializar la API con metadata
app = FastAPI(
    title="DB Migration API",
    description="API para migración de datos desde CSV a SQL Server",
    version="1.0.0"
)

# Registrar las rutas definidas en routes.py
app.include_router(router)

# Ruta de prueba para comprobar que la API funciona
@app.get("/")
def home():
    return {"message": "API funcionando correctamente"}