from fastapi import APIRouter, UploadFile, File
import shutil
import pandas as pd
import os
from app.db import conn, cursor

router = APIRouter()

# 🔹 Endpoint para subir archivos CSV
@router.post("/upload_csv/")
async def upload_csv(file: UploadFile = File(...)):
    file_path = f"data/{file.filename}"
    os.makedirs("data", exist_ok=True)  # Asegura que el directorio exista

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": f"Archivo {file.filename} cargado correctamente"}

# 🔹 Endpoint para importar datos desde CSV a la base de datos
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
        # Importar departamentos
        df_departments = pd.read_csv(files["departments"], encoding="utf-8")
        cursor.executemany("INSERT INTO Departments (department_id, DepartmentName) VALUES (?, ?)",
                           df_departments[["department_id", "DepartmentName"]].values.tolist())

        # Importar trabajos
        df_jobs = pd.read_csv(files["jobs"], encoding="utf-8")
        cursor.executemany("INSERT INTO Jobs (job_id, JobName) VALUES (?, ?)",
                           df_jobs[["job_id", "JobName"]].values.tolist())

        # Importar empleados
        df_hired = pd.read_csv(files["employees"], encoding="utf-8")
        cursor.executemany("INSERT INTO HiredEmployees (id, name, date, department_id, job_id) VALUES (?, ?, ?, ?, ?)",
                           df_hired[["id", "name", "date", "department_id", "job_id"]].values.tolist())

        conn.commit()
        return {"message": "Datos importados correctamente a todas las tablas"}
    
    except Exception as e:
        return {"error": f"Error al importar datos: {e}"}

# 🔹 Endpoint para insertar registros en batch con validación de tamaño
@router.post("/batch_insert/")
async def batch_insert():
    path = "data/hired_employees.csv"

    if not os.path.exists(path):
        return {"error": "El archivo hired_employees.csv no existe"}

    df = pd.read_csv(path, encoding="utf-8")

    if len(df) > 1000:
        return {"error": "Máximo 1000 filas por inserción"}

    try:
        cursor.executemany("INSERT INTO HiredEmployees (id, name, date, department_id, job_id) VALUES (?, ?, ?, ?, ?)",
                           df[["id", "name", "date", "department_id", "job_id"]].values.tolist())

        conn.commit()
        return {"message": f"Se insertaron {len(df)} registros correctamente"}
    
    except Exception as e:
        return {"error": f"Error al insertar registros en batch: {e}"}

# 🔹 Endpoint para consultar empleados contratados por trabajo y departamento en 2021, por trimestre
@router.get("/hired_by_quarter/")
async def hired_by_quarter():
    cursor.execute("""
        SELECT 
            d.DepartmentName AS department,
            j.JobName AS job,
            SUM(CASE WHEN MONTH(h.date) BETWEEN 1 AND 3 THEN 1 ELSE 0 END) AS Q1,
            SUM(CASE WHEN MONTH(h.date) BETWEEN 4 AND 6 THEN 1 ELSE 0 END) AS Q2,
            SUM(CASE WHEN MONTH(h.date) BETWEEN 7 AND 9 THEN 1 ELSE 0 END) AS Q3,
            SUM(CASE WHEN MONTH(h.date) BETWEEN 10 AND 12 THEN 1 ELSE 0 END) AS Q4
        FROM HiredEmployees h
        JOIN Departments d ON h.department_id = d.department_id
        JOIN Jobs j ON h.job_id = j.job_id
        WHERE YEAR(h.date) = 2021
        GROUP BY d.DepartmentName, j.JobName
        ORDER BY d.DepartmentName, j.JobName;
    """)
    
    columns = [column[0] for column in cursor.description]  # Obtener nombres de columnas
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]  # Convertir a lista de diccionarios

    return results

# 🔹 Endpoint para consultar departamentos que contrataron más empleados que el promedio en 2021
@router.get("/above_average_hiring/")
async def above_average_hiring():
    cursor.execute("""
        WITH DeptAverage AS (
            SELECT AVG(hired_count) AS avg_hired
            FROM (
                SELECT department_id, COUNT(*) AS hired_count
                FROM HiredEmployees
                WHERE YEAR(date) = 2021
                GROUP BY department_id
            ) AS subquery
        )
        SELECT d.department_id, d.DepartmentName AS department, COUNT(*) AS hired
        FROM HiredEmployees h
        JOIN Departments d ON h.department_id = d.department_id
        WHERE YEAR(h.date) = 2021
        GROUP BY d.department_id, d.DepartmentName
        HAVING COUNT(*) > (SELECT avg_hired FROM DeptAverage)
        ORDER BY hired DESC;
    """)
    
    columns = [column[0] for column in cursor.description]  # Obtener nombres de columnas
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]  # Convertir a lista de diccionarios

    return results