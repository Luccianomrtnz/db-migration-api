
```markdown
# 📌 API de Migración de Datos  

## 🚀 Descripción  
Esta API permite subir archivos CSV, importar datos a una base de datos SQL Server y consultar información sobre contrataciones por trimestre y departamentos con contrataciones superiores al promedio.  

## 📌 Instalación  
### 🔹 Clona el repositorio  
```sh
git clone https://github.com/tuusuario/db-migration-api.git
```
### 🔹 Accede al directorio del proyecto  
```sh
cd db-migration-api
```
### 🔹 Instala las dependencias  
```sh
pip install -r requirements.txt
```

## 🔥 Uso  
### 🔹 Ejecutar la API localmente  
```sh
uvicorn app.main:app --reload
```
### 🔹 Probar los endpoints con `curl` o Postman  
```sh
curl -X GET http://localhost:8000/hired_by_quarter/
```
### 🔹 Ejecutar pruebas  
```sh
pytest test_api.py
```



## 🎯 Autor  
✍️ **Luciano** 🚀  
```

🔥 **¡Pégalo directamente en tu proyecto y sube los cambios a GitHub!** 🚀💪  
🎯 **Si necesitas algún ajuste, dime y lo hacemos juntos.** 😎  
🚀 **¿Quieres avanzar con Docker después de esto?**  
