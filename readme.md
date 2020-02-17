# Instrucciones de instalación
1. Clonamos el proyecto Tkinter
```
- git clone 'ruta', donde 'ruta' es la indicada en el formulario de entrega
```

2. Creación y activación del entorno virtual

3. Instalar las dependencias del fichero requirements.txt
```
pip install -r requirements.txt
```

4. Creación de la base de datos
```
- Creamos el directorio data dentro de la 'ruta' del proyecto
- Tecleamos sqlite3 'nombredelaBD'
- Tecleamos .read ../migrations/createtables.sql
```

5. Generación de la clave API
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