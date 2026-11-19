# EL CODIGO A CONTINUACION TIENE COMO FUNCION ELIMINAR CLIENTES DE: *VERDER*
def ELIMINAR_CLIENTES():
    try:
        # IMPORTACION DE LIGRERIAS.
        import os
        from dotenv import load_dotenv
        import mysql.connector
        from tkinter import messagebox

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

        # CARGA LA INFORMACION DEL .env
        load_dotenv(r"C:\Users\Usuario\OneDrive\Documentos\.Codigos\.env")

        # CONEXION MySQL.
        connection = {
            'user': os.environ.get('DB_USER'),
            'password': os.environ.get('DB_PASSWORD'),
            'host': os.environ.get('DB_HOST'),
            'database': os.environ.get('DB_NAME'),
            'port': 3306
        }

        # COMIENZO DEL BUCLE
        while True:

            # SE LE PREGUNTA AL USUARIO EL NOMBRE DEL CLIENTE QUE DESEA ELIMINAR
            cliente= input('\n\nINGRESE EL NOMBRE EXACTO DEL CLIENTE QUE DESEA ELIMINAR: ')
            
            # SE ABRE LA CONECCION CON LA BASE DE DATOS.
            with mysql.connector.connect(**connection) as conn:
                cur = conn.cursor()

                #SE VERIFICA LA EXISTENCIA DE EL CLIENTE.
                cur.execute('SELECT clientes FROM _systema_web_clientes WHERE clientes = %s', (cliente,))
                confirmacion = cur.fetchall()
                if not confirmacion:
                    print(f'\nEl cliente ingresado no fue encontrado dentro dee la base dde datos.\n')
                    seleccion= input(' ENTER PARA CONTINUAR\n 1 + ENTER PARA IR AL MENU\n')
                    if seleccion == '1': break
                    else: continue

                # SE ELIMINA LA LINEA EXISTENTE DEL CLIENTE INDICADO.
                cur.execute('DELETE FROM _systema_web_clientes WHERE clientes = %s', (cliente,))
                conn.commit()

            # AVISO DE FINALIZACION, PERMITE REGRESAR AL MENU O CONTINUAR.
            print(f'\nEl cliente fue eliminado exitosamente.\nCliente Eliminado: {cliente}\n')
            seleccion= input(' ENTER PARA CONTINUAR\n 1 + ENTER PARA IR AL MENU\n')
            if seleccion == '1': break
            else: continue
            
    except Exception as e:
        print(f'ERROR:\n{e}\n')
        input(' ENTER\n')