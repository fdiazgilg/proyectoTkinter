# Instrucciones de instalación

1. Creación y activación del entorno virtual

2. Instalar las dependencias del fichero requirements.txt
```
pip install -r requirements.txt
```

3. Creación de la base de datos
```
Nos situamos en el directorio ./data
comando sqlite3 nombredelabd
.read ruta relativa del fichero ../migrations/creatables.sql
```

4. Modificación del fichero de configuración
```
Generar un APIKEY en la página de CoinMarket, https://coinmarketcap.com/api/
Con dicho valor actualizaremos la clave SECRET_KEY del fichero config.ini.example
Actualizar la clave DB_FILE con el nombre de nuestra base de datos
Renombrar config.ini.example como config.ini
```

5. Lanzar la aplicación
```
python main.py
```