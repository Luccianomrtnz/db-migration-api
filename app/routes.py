from fastapi import APIRouter, UploadFile, File
import shutil
import pandas as pd
import os
from app.db import conn, cursor

router = APIRouter()

# ✅ Endpoint para subir archivos CSV con validación de existencia
@router.post("/upload_csv/")
async def upload_csv(file: UploadFile = File(...)):
    file_path = f"data/{file.filename}"
    os.makedirs("data", exist_ok=True)  # Asegura que el directorio exista

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": f"Archivo {file.filename} cargado correctamente"}

# ✅ Endpoint para importar datos de múltiples CSV con manejo de errores
@router.post("/import_data/")
async def import_data():
    files = {
        "departments": "data/departments.csv",
        "jobs": "data/jobs.csv",
        "employees": "data/hired_employees.csv"
    }

    for name, path in files.items():
        if not os.path.exists(path):
            return {"error": f"El archivo {name}.csv no existe"}

    try:
        # 🔹 Importar departamentos
        df_departments = pd.read_csv(files["departments"], encoding="utf-8")
        cursor.executemany("INSERT INTO Departments (department_id, DepartmentName) VALUES (?, ?)",
                           df_departments[["department_id", "DepartmentName"]].values.tolist())

        # 🔹 Importar trabajos
        df_jobs = pd.read_csv(files["jobs"], encoding="utf-8")
        cursor.executemany("INSERT INTO Jobs (job_id, JobName) VALUES (?, ?)",
                           df_jobs[["job_id", "JobName"]].values.tolist())

        # 🔹 Importar empleados
        df_hired = pd.read_csv(files["employees"], encoding="utf-8")
        cursor.executemany("INSERT INTO HiredEmployees (id, name, date, department_id, job_id) VALUES (?, ?, ?, ?, ?)",
                           df_hired[["id", "name", "date", "department_id", "job_id"]].values.tolist())

        conn.commit()
        return {"message": "Datos importados correctamente a todas las tablas"}
    
    except Exception as e:
        return {"error": f"Error al importar datos: {e}"}

# ✅ Endpoint para insertar registros en batch con validación de tamaño y eficiencia
@router.post("/batch_insert/")
async def batch_insert():
    path = "data/hired_employees.csv"

    if not os.path.exists(path):
        return {"error": "El archivo hired_employees.csv no existe"}

    df = pd.read_csv(path, encoding="utf-8")  # Leer CSV con codificación

    if len(df) > 1000:
        return {"error": "Máximo 1000 filas por inserción"}

    try:
        cursor.executemany("INSERT INTO HiredEmployees (id, name, date, department_id, job_id) VALUES (?, ?, ?, ?, ?)",
                           df[["id", "name", "date", "department_id", "job_id"]].values.tolist())

        conn.commit()
        return {"message": f"Se insertaron {len(df)} registros correctamente"}
    
    except Exception as e:
        return {"error": f"Error al insertar registros en batch: {e}"}