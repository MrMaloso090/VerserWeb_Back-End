import mysql.connector
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import os

# Carga las variables del .env
load_dotenv()
# CONECCION MySQL.
connection = {
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'database': os.environ.get('DB_NAME'),
    'port': 3306}


# DEF PARA TOMAR TODOS LOS DATOS DE LA TABLA QUE SE INDIQUE.
def importar_tabla_mysql(tabla):
    with mysql.connector.connect(**connection) as conn:
        cur= conn.cursor(buffered=True)
        cur.execute(f'SELECT * FROM {tabla}')
        listado_raw = cur.fetchall()
        nombres = [descripcion[0] for descripcion in cur.description]
        listado = [dict(zip(nombres, fila)) for fila in listado_raw]
        return jsonify(listado)


# DEF PARA EL RECONOCIMIENTO DE USUARIOS VALIDOS
def login_usuarios():
    data = request.get_json()
    cod = data.get("codigo")
    pag = data.get("pag")

    try:
        with mysql.connector.connect(**connection) as conn:
            cur = conn.cursor(buffered=True)
            cur.execute(f'SELECT usuario, {pag} FROM _systema_web_usuarios WHERE codigo= %s', (cod,))        
            datos = cur.fetchone()
            if not datos: return jsonify({'valido': False}), 401

            nombre = datos[0]
            pagina = datos[1]
            if pagina != 1: return jsonify({'valido': False}), 401
            
            return jsonify({'valido': True, 'nombre': nombre})
    except Exception as e:
        return jsonify({"error": "Error interno (falla en back-end)"}), 500