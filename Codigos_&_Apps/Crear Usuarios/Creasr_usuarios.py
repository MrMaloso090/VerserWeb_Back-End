def CREEAR_USUARIO(
usuario,
ingresos,
salidas,
dannos,
reprocesos,
___registro_de_control_ar,
___registro_de_control_bisel,
___registro_de_control_calidad,
___registro_de_control_digitacion,
___registro_de_control_facturacion,
___registro_de_control_ingresos,
___registro_de_control_talla,
___registro_de_control_coating,
___registro_de_control_inventario,
___registro_de_control_ingresos_logisticos):

    import os
    from dotenv import load_dotenv
    import mysql.connector
    import random

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
        'port': 3306}

    # SE HACE UN BUCLE QUE GENERA CODIGOS RANDOM HASTA QUE SALGA UNO QUE YA NO ESTE USADO. ESTA ES LA CONTRASE;A.
    with mysql.connector.connect(**connection) as  conn:
        cur = conn.cursor()

        cur.execute('SELECT 1 FROM _systema_web_usuarios WHERE usuario= %s', (usuario,))
        existente = cur.fetchone()
        if existente: 
            print(f' - El nombre de usuario={usuario} ya se encuentra en uso - ')
            input('ENTER')
            return
        
        while True:
            codigo = random.randint(100000, 999999)  #Genera cualquier codigo de 6 digitos.

            cur.execute('SELECT 1 FROM _systema_web_usuarios WHERE codigo= %s', (codigo,))
            comprobante = cur.fetchone()
            if not comprobante: break

        # SE INGRESA LA INFORMACION DENTRO DE LA BASE DE DATOS
        cur.execute("""
        INSERT INTO _systema_web_usuarios(
            codigo, 
            usuario, 
            ingresos, 
            salidas, 
            dannos, 
            reprocesos,
            ___registro_de_control_ar,
            ___registro_de_control_bisel,
            ___registro_de_control_calidad,
            ___registro_de_control_digitacion,
            ___registro_de_control_facturacion,
            ___registro_de_control_ingresos,
            ___registro_de_control_talla,
            ___registro_de_control_coating,
            ___registro_de_control_inventario,
            ___registro_de_control_ingresos_logisticos)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (
            codigo, 
            usuario, 
            ingresos, 
            salidas, 
            dannos, 
            reprocesos,
            ___registro_de_control_ar,
            ___registro_de_control_bisel,
            ___registro_de_control_calidad,
            ___registro_de_control_digitacion,
            ___registro_de_control_facturacion,
            ___registro_de_control_ingresos,
            ___registro_de_control_talla,
            ___registro_de_control_coating,
            ___registro_de_control_inventario,
            ___registro_de_control_ingresos_logisticos))
        conn.commit()

    print('Terminado')
    return




CREEAR_USUARIO(
    'CALIDAD (David)',
    0,
    1,
    1,
    1,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0
)