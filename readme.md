# Instrucciones de instalación

1. Creación y activación del entorno virtual

2. Instalar las dependencias del fichero requirements.txt
```
pip install -r requirements.txt
```

3. Creación de la base de datos
```
- Desde la ruta base creamos el directorio data
- Nos situamos dentro del directorio data 
- Nos situamos en el directorio ./data
- Tecleamos sqlite3 'nombredelaBD'
- Tecleamos read ../migrations/createtables.sql
```

4. Generación de la clave API
```
- Generamos un APIKEY en la página de CoinMarket, https://coinmarketcap.com/api/
```

5. Modificación del fichero de configuración
```
- Actualizamos la clave SECRET_KEY del fichero config.ini.example
- Actualizamos la clave DB_FILE con el nombre de nuestra base de datos
- Renombramos el fichero config.ini.example como config.ini
```

6. Lanzar la aplicación
```
python main.py
```