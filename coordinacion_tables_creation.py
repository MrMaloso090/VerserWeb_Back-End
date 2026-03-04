# SUGIERO QUE ANTES DE CORRER ESTE CODIGO, YA HAYAS CREADO LAS OTRAS TABLAS.
import mysql.connector
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

# DICCIONARIOS DE COLUMNAS PARA CADA TABLA.
dic__registro_de_control_bisel = {
    'id': 'INT NOT NULL AUTO_INCREMENT PRIMARY KEY',
    'fecha_hora': 'DATETIME',
    'id_responsable': 'INT',
    'id_break': 'INT',
    'calibracion_limpieza_de_maquinas_solucion_de_novedades': 'INT',
    'cantidad_de_bisel_especial': 'INT',
    'cantidad_de_bisel_general': 'INT',
    'montaje': 'INT',
    'cantidad_de_arreglos': 'INT',
    'cantidad_de_limpieza_normal': 'INT',
    'limpieza_de_ranura': 'INT',
    'ensamble_de_tres_piezas': 'INT',
    'cantidad_de_bloqueados': 'INT',
    'observaciones': 'VARCHAR(250)'
}
dic__registro_de_control_talla = {
    'id': 'INT NOT NULL AUTO_INCREMENT PRIMARY KEY',
    'fecha_hora': 'DATETIME',
    'id_responsable': 'INT',
    'id_break': 'INT',
    'calibracion_limpieza_de_maquinas_solucion_de_novedades': 'INT',
    'cantidad_de_encintado': 'INT',
    'cantidad_de_bloqueo': 'INT',
    'cantidad_de_pulido': 'INT',
    'reprocesos': 'INT',
    'observaciones': 'VARCHAR(250)'
}
dic__registro_de_control_ar = {
    'id': 'INT NOT NULL AUTO_INCREMENT PRIMARY KEY',
    'fecha_hora': 'DATETIME',
    'id_responsable': 'INT',
    'id_break': 'INT',
    'id_tratamiento': 'INT',
    'calibracion_limpieza_de_maquinas_solucion_de_novedades': 'INT',
    'cantidad_de_lentes_por_ciclo': 'INT',
    'numero_del_ciclo': 'INT',
    'hora_de_inicio': 'TIME',
    'hora_de_salida': 'TIME',
    'inventario': 'VARCHAR(250)',
    'observaciones': 'VARCHAR(250)'
}
dic__registro_de_control_ingresos = {
    'id': 'INT NOT NULL AUTO_INCREMENT PRIMARY KEY',
    'fecha_hora': 'DATETIME',
    'id_responsable': 'INT',
    'id_break': 'INT',
    'calibracion_limpieza_de_maquinas_solucion_de_novedades': 'INT',
    'cantidad_de_ingresos': 'INT',
    'revision_de_terminados': 'INT',
    'observaciones': 'VARCHAR(250)'
}
dic__registro_de_control_digitacion = {
    'id': 'INT NOT NULL AUTO_INCREMENT PRIMARY KEY',
    'fecha_hora': 'DATETIME',
    'id_responsable': 'INT',
    'id_break': 'INT',
    'calibracion_limpieza_de_maquinas_solucion_de_novedades': 'INT',
    'cantidad_de_suministros': 'INT',
    'cantidad_de_digitados': 'INT',
    'inventario': 'VARCHAR(250)',
    'observaciones': 'VARCHAR(250)'
}
dic__registro_de_control_facturacion = {
    'id': 'INT NOT NULL AUTO_INCREMENT PRIMARY KEY',
    'fecha_hora': 'DATETIME',
    'id_responsable': 'INT',
    'id_break': 'INT',
    'otras_actividades': 'INT',
    'cantidad_de_facturados': 'INT',
    'cantidad_de_empacados': 'INT',
    'inventario': 'VARCHAR(250)',
    'observaciones': 'VARCHAR(250)'
}
dic__registro_de_control_calidad = {
    'id': 'INT NOT NULL AUTO_INCREMENT PRIMARY KEY',
    'fecha_hora': 'DATETIME',
    'id_responsable': 'INT',
    'id_break': 'INT',
    'tiempo_calibracion_limpieza_de_maquinas_solucion_de_novedades': 'INT',
    'control_inicial_de_coating': 'INT',
    'control_inicial_de_bisel': 'INT',
    'control_final': 'INT',
    'empaquetado': 'INT',
    'reprocesos': 'INT',
    'inventario': 'VARCHAR(250)',
    'observaciones': 'VARCHAR(250)'
}

# DICCIONARIO DE DICCIONARIOS CON LOS NOMBRES DE LAS TABLAS.
tables = {
    '___registro_de_control_bisel': dic__registro_de_control_bisel,
    '___registro_de_control_talla': dic__registro_de_control_talla,
    '___registro_de_control_ar': dic__registro_de_control_ar,
    '___registro_de_control_ingresos': dic__registro_de_control_ingresos,
    '___registro_de_control_digitacion': dic__registro_de_control_digitacion,
    '___registro_de_control_facturacion': dic__registro_de_control_facturacion,
    '___registro_de_control_calidad': dic__registro_de_control_calidad
}

# definicion que tomara los nombre de las columnas que comienzan con id y creara una tabla para normalizar, en caso de que aun no exista.
def create_normaliced_tables(name, cur):
    cur.execute(f'CREATE TABLE IF NOT EXISTS __{name[3:]} (id INT AUTO_INCREMENT PRIMARY KEY, {name[3:]} VARCHAR(250) UNIQUE NOT NULL)')

# DEFINICION DEL LOOP QUE PROCESARA LA CREACION DE LAS TABLAS.
def creation(tables):
    with mysql.connector.connect(**connection) as conn:
        cur= conn.cursor()

        for name, table in tables.items():
            columns_list= []
            for column_name, column_type in table.items():
                if column_name.startswith('id_'):
                    create_normaliced_tables(column_name, cur)
                columns_list.append(f'`{column_name}` {column_type}')
                
            columns_text= ', '.join(columns_list)
            cur.execute(f'CREATE TABLE `{name}` ({columns_text})')
            print('.')

        conn.commit()
        print('033[31mTABLAS CREADAS CORRECTAMENTE033[0m')

# EJECUCION.
creation(tables)