# EJECUCION DEL PROCESO QUE AGREGA LAS SALIDAS.
def PROCESO():
    import os
    from dotenv import load_dotenv
    import mysql.connector
    import pandas
    from datetime import datetime

    # LIBRERIAS IMPORTADAS PARA QUE *EL .EXE FUNCIONE EN COMPUTADORES SIN PYTHON.
    import sys
    import mysql.connector
    import mysql.connector.plugins.mysql_native_password
    import mysql.connector.locales.eng
    import cryptography
    import certifi
    import win32security
    if getattr(sys, "frozen", False):
        ruta_base = sys._MEIPASS
    else:
        ruta_base = os.path.dirname(os.path.abspath(__file__))

    # Carga las variables del .env
    load_dotenv(r"C:\Users\Usuario\OneDrive\Documentos\.Codigos\.env")
    # CONEXION MySQL.
    connection = {
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'host': os.environ.get('DB_HOST'),
        'database': os.environ.get('DB_NAME'),
        'port': 3306
    }

    # SE TOMAN LOS DATOS DEL EXCEL.
    data_frame = pandas.read_excel('Salidas.xlsx')

    # Convierte la columna a fecha por si viene como texto.
    data_frame['salida'] = pandas.to_datetime(
        data_frame['salida'],
        errors='coerce'
    )

    # Elimina filas con fechas invAlidas.
    data_frame = data_frame.dropna(subset=['salida'])

    ordenes = list(data_frame['#Orden'])
    salidas = list(data_frame['salida'])

    with mysql.connector.connect(**connection) as conn:
        cur = conn.cursor()

        for ORDEN, SALIDA in zip(ordenes, salidas):

            ORDEN = int(ORDEN)

            # FILTROS.
            cur.execute(
                'SELECT 1 FROM _ingresos_y_salidas WHERE numero_de_orden = %s',
                (ORDEN,)
            )
            exist = cur.fetchone()

            if not exist:
                print(f'La Orden #{ORDEN} no se encuentra dentro de _ingresos_y_salidas')
                continue

            cur.execute(
                'SELECT fecha FROM _ingresos_y_salidas WHERE numero_de_orden = %s',
                (ORDEN,)
            )
            ingreso = cur.fetchone()

            ingreso = ingreso[0]

            if not ingreso:
                print(f'La Orden #{ORDEN} no cuenta con una fecha de ingreso.')
                continue

            ingreso = pandas.to_datetime(ingreso)

            tardanza = (SALIDA.date() - ingreso.date()).days

            if tardanza < 0:
                print(
                    f'La Orden #{ORDEN} genera una Tardanza negativa: {tardanza}\n'
                    f'Ingreso: {ingreso}\n'
                    f'Salida: {SALIDA}'
                )
                continue

            # SE AGREGA LA FECHA DE SALIDA.
            salida_mysql = SALIDA.strftime("%Y-%m-%d %H:%M:%S")

            cur.execute(
                '''
                UPDATE _ingresos_y_salidas
                SET fecha_de_salida = %s,
                    tardanza = %s
                WHERE numero_de_orden = %s
                ''',
                (salida_mysql, tardanza, ORDEN)
            )

            conn.commit()

            print(f"#{ORDEN}: Guardado correctamente")

    print('========================================')
    input('Enter para cerrar.')

# SE CORRE EL PROCESO.
PROCESO()