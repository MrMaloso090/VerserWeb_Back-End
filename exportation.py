import mysql.connector
from flask import Flask, jsonify, request
from datetime import datetime
import pytz
import traceback
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


# CREACION DE LAS TABLAS EN CASO DE SER NECESARIO (OJALA QUE NUNCA JAJA, PERO AHI ESTA)
def all__SQL_tables_creation():

    # FUNCION PARA CREAR LAS TABLAS PRINCIPALES.
    def create_table(NOMBRE_TABLA, COLUMNAS):
        columns_list = []
        for nombre, tipo in COLUMNAS.items():
            columns_list.append(f'{nombre} {tipo}')
        columns = ', '.join(columns_list)
        with mysql.connector.connect(**connection) as conn:
            cur = conn.cursor(buffered=True)
            cur.execute(f'CREATE TABLE IF NOT EXISTS `{NOMBRE_TABLA}`({columns})')

    # FUNCION PARA CREAR LAS TABLAS SUPLEMENTARIAS (MANY TO ONE)
    def normalization_tables(SUPPORT_TABLE):
        with mysql.connector.connect(**connection) as conn:
            cur = conn.cursor(buffered=True)
            cur.execute(f'CREATE TABLE IF NOT EXISTS {SUPPORT_TABLE}(id INT AUTO_INCREMENT PRIMARY KEY, {SUPPORT_TABLE} VARCHAR(250) UNIQUE NOT NULL)')

    # TABLAS PRINCIPALES.
    ingresos_y_salidas_dic = {
        'numero_de_orden':'BIGINT PRIMARY KEY', 
        'id_cliente': 'INT',
        'numero_de_gaveta': 'VARCHAR(250)',
        'id_tipo_de_ingresos': 'INT',
        'id_motivo_de_garantia': 'INT',
        'orden_de_origen_de_la_garantia': 'INT',
        'id_tipo_de_lente': 'INT',
        'id_ar': 'INT',
        'id_estado_de_montura': 'INT',
        'id_condicion_especial': 'INT',
        'fecha': 'VARCHAR(250)',
        'fecha_de_salida': 'VARCHAR(250)',
        'tardanza': 'INT',
        'id_usuario': 'INT',
        'id_usuario_salida': 'INT',
        'nota': 'TEXT',
        'nota_de_salida': 'TEXT'
    }
    dannos_dic = {
        'numero_de_orden':'BIGINT', 
        'id_area_responsable': 'INT',
        'id_cliente': 'INT',
        'id_lente': 'INT',
        'id_motivo': 'INT',
        'id_responsable': 'INT',
        'id_material': 'INT',
        'numero_de_gaveta': 'VARCHAR(250)',
        'observaciones': 'VARCHAR(250)',
        'fecha': 'VARCHAR(250)',
        'costo': 'INT',
        'id_usuario': 'INT'
    }
    reprocesos_dic = {
        'numero_de_orden':'BIGINT', 
        'id_area_responsable': 'INT',
        'id_cliente': 'INT',
        'id_lente': 'INT',
        'id_motivo': 'INT',
        'id_material': 'INT',
        'numero_de_gaveta': 'VARCHAR(250)',
        'observaciones': 'VARCHAR(250)',
        'fecha': 'VARCHAR(250)',
        'id_usuario': 'INT'
    }

    # CREACION DE 3 LAS TABLAS PRINCIPALES.
    create_table('_ingresos_y_salidas', ingresos_y_salidas_dic)
    create_table('_dannos', dannos_dic)
    create_table('_reprocesos', reprocesos_dic)

    #CREACION DE LAS TABLAS SUPLEMENTARIAS MANY TO ONE.
    normalization_tables('cliente')
    normalization_tables('tipo_de_ingresos')
    normalization_tables('motivo_de_garantia')
    normalization_tables('tipo_de_lente')
    normalization_tables('ar')
    normalization_tables('estado_de_montura')
    normalization_tables('condicion_especial')
    normalization_tables('area_responsable')
    normalization_tables('lente')
    normalization_tables('motivo')
    normalization_tables('responsable')
    normalization_tables('material')
    normalization_tables('usuario')
    normalization_tables('usuario_salida')


# DEF PARA AGREGAR LOS DATOS DE LOS QUESTIONARIOS A LA BASE DE DATOS MySQL. *** NO GUARDA LAS SALIDAS ***
def guardado_idr():
    data = request.get_json()

    normalized_columns= ('cliente', 'tipo_de_ingresos', 'motivo_de_garantia', 'tipo_de_lente', 'ar', 'estado_de_montura', 
                         'condicion_especial', 'area_responsable', 'lente', 'motivo', 'responsable', 'material', 'usuario')
    
    columns_list=[]
    values_list=[]
    with mysql.connector.connect(**connection) as conn:
        cur= conn.cursor(buffered=True)

        table= data.get('tabla')

        # COMPROBANTE DE QUE EL NUMERO DE ORDEN NO SE ENCUENTRA EN LA BASE DE DATOS, EN TAL CASO, MANDAR ERROR.
        numero= data.get('numero_de_orden')
        
        if table == '_ingresos_y_salidas':
            cur.execute(f'SELECT * FROM {table} WHERE numero_de_orden= %s', (numero,))
            used= cur.fetchone()
            if used:
                return jsonify({'error': 'Este numero de orden ya se encuentra registrado'}), 400 # MANDA ERROR.
            
            # COMPROBANTE DE QUE EL NUMERDO DE ORIGEN DE LA GARANTIA SI SE ENCUENTRE REGISTRADO COMO UNA ENTRADA ANTERIOR.
            #orden_de_origen = data.get('orden_de_origen_de_la_garantia')
            #if orden_de_origen:
            #    cur.execute('SELECT * FROM _ingresos_y_salidas WHERE numero_de_orden = %s', (orden_de_origen,))
            #    listed_order = cur.fetchone()
            #    
            #    if listed_order is None:
            #        return jsonify({'error': 'El número de *Orden de Origen de la Garantía* no se encuentra registrado como un ingreso previo existente.'}), 400 # MANDA ERROR.
                
        
        # COMPRUEVA QUE EL NUMERO DE ORDEN INGRESADO EN *DANNOS* O *REPROCESOS* SE ENCUENTRE PREVIAMENTE INGRESADO EN LA TABLA DE INGRESOS
        if table == '_dannos' or table == '_reprocesos':
            cur.execute('SELECT id_cliente, numero_de_gaveta FROM _ingresos_y_salidas WHERE numero_de_orden= %s', (numero,))
            tupla = cur.fetchone()

            if not tupla:
                return jsonify({'error': 'Este numero de orden no se encuentra registrado entre los ingresos'}), 400 # MANDA ERROR.
            
            # AGREGA EL CLIENTE Y LA GAVETA DEL RESPECTIVO NUMERO DE ORDEN Y LO CUARDA EN LAS LISTAS PARA SER AGREGADOS A SU TABLA
            id_c = tupla[0]
            g = tupla[1]

            columns_list.append('id_cliente')
            values_list.append(id_c)
            columns_list.append('numero_de_gaveta')
            values_list.append(g)

        try:
            for key, value in data.items():
                if key == 'tabla': continue

                if key in normalized_columns:
                    cur.execute(f'SELECT id FROM {key} WHERE {key}= %s', (value,))
                    id= cur.fetchone()
                    if not id:
                        cur.execute(f'INSERT IGNORE INTO {key}({key}) VALUES(%s)', (value,))
                        conn.commit()
                        cur.execute(f'SELECT id FROM {key} WHERE {key}= %s', (value,))
                        id= cur.fetchone()

                    if id: id= id[0]
                    else: id= None
                    
                    columns_list.append(f'id_{key}')
                    values_list.append(id)
                    continue

                columns_list.append(key)
                values_list.append(value)

            columns_list.append('fecha')
            values_list.append(datetime.now(pytz.timezone('America/Bogota')).strftime("%Y-%m-%d %H:%M"))


            # FUNCION PARA CALCULAR EL PRECIO DE LOS DANNOS
            if table == '_dannos':
                lente= data.get('lente')
                material= data.get('material')
                if lente != 'AO': cantidad= 1
                else: cantidad= 2

                cur.execute('SELECT costo FROM _systema_web_costo_materiales WHERE material=%s', (material,))
                costo_material= cur.fetchone()
                costo_final= costo_material[0] * cantidad

                columns_list.append('costo')
                values_list.append(costo_final)
            # *FINAL* DE LA FUNCION QUE CALCULAR EL PRECIO DE LOS DANNOS


            colums= ', '.join(columns_list)
            indicator_list= (['%s'] * len(values_list))
            indicator= ', '.join(indicator_list)
            
            cur.execute(f'INSERT INTO {table}({colums}) VALUES({indicator})', values_list)
            conn.commit()
        except Exception as e:
            error_detalle = traceback.format_exc()
            return jsonify({
                'error': f'ERROR INESPERADO AL GUARDAR LA INFORMACION DENTRO DE LA BASE DE DATOS \n{str(e)} \n{error_detalle}'
            }), 400

        return jsonify({'complete': 'Los datos se han guardado correctamente'}) # MENSAGE DE VALIDACION


# DEF PARA GUARDAR LA FECHA DE **SALIDA** DE SU RESPECTTIVO NUMERO DE ORDEN.
def guardado_s():
    data = request.get_json()
    numero = data.get('numero_de_orden')
    nota_de_salida = data.get('nota_de_salida')
    usuario_salida = data.get('usuario')

    with mysql.connector.connect(**connection) as conn:
        cur= conn.cursor(buffered=True)   

        cur.execute('SELECT numero_de_orden, fecha_de_salida, fecha  FROM _ingresos_y_salidas WHERE numero_de_orden= %s', (numero,))
        respuesta= cur.fetchone()

        if not respuesta: 
            return jsonify({'error': 'Este numero de orden no se encuentra registrado'}), 400 # MANDA ERROR.
        
        if respuesta[1]:
            return jsonify({'error': f'Este numero de orden ya tiene una fecha de salida: -{respuesta[1]}-'}), 400 # MANDA ERROR.
        
        try:
            fecha_de_ingreso = datetime.strptime(str(respuesta[2]), "%Y-%m-%d %H:%M")
            fecha_de_salida = datetime.now(pytz.timezone('America/Bogota')).replace(second=0, microsecond=0)
            tardanza = (fecha_de_salida.date() - fecha_de_ingreso.date()).days
            
            fecha_de_salida = fecha_de_salida.strftime("%Y-%m-%d %H:%M")
        except Exception as e:
            return jsonify({'error': f'ERROR INESPERADO AL GUARDAR LA INFORMACION DENTRO DE LA BASE DE DATOS, ERROR AL INTENTAR ECONCONTRAR LA TARDANZA ENTRE LAS FECHAS \n{e}'}), 400 # MANDA ERROR.
        
        try:
            cur.execute('SELECT id FROM usuario_salida WHERE usuario_salida = %s', (usuario_salida,))
            id_usuario_salida = cur.fetchone()
            if not id_usuario_salida:
                cur.execute('INSERT IGNORE INTO usuario_salida(usuario_salida) VALUES(%s)', (usuario_salida,))
                conn.commit()
                cur.execute('SELECT id FROM usuario_salida WHERE usuario_salida = %s', (usuario_salida,))
                id_usuario_salida = cur.fetchone()

            if id_usuario_salida: id_usuario_salida = id_usuario_salida[0]
            else: id_usuario_salida = None


            cur.execute('UPDATE _ingresos_y_salidas SET fecha_de_salida = %s, tardanza = %s, id_usuario_salida = %s, nota_de_salida = %s WHERE numero_de_orden = %s', (fecha_de_salida, int(tardanza), id_usuario_salida, nota_de_salida, numero))
            conn.commit()
        except Exception as e:
            return jsonify({'error': f'ERROR INESPERADO AL GUARDAR LA INFORMACION DENTRO DE LA BASE DE DATOS \n{e}'}), 400 # MANDA ERROR.
        
        return jsonify({'complete': 'Los datos se han guardado correctamente'}) # MENSAGE DE VALIDACION
    

# DEFINICION QUE TOMA LOS DATOS DE TODOS LOS DOCUMENTOS DE COORDINACION PARA CARGARLOS EN LA BASE DE DATOS, ESTA FUNCION ES GENERAL PARA TODOS LOS DOCUMENTOS DE COORDINACION.
def coordinacion_exportacion_general():
    data= request.get_json()
    table = data.get('titulo')
    with mysql.connector.connect(**connection) as conn:
        cur= conn.cursor()

        try:
            normalized_columns= ('responsable', 'break', 'tratamiento', 'numero_del_ciclo')
            column_list = []
            valeu_list = []
            for column, valeu in data.items():
                if column == 'titulo': continue

                if column in normalized_columns:
                    cur.execute(f'SELECT id FROM __{column} WHERE {column}= %s', (valeu,))
                    id= cur.fetchone()
                    if not id:
                        cur.execute(f'INSERT IGNORE INTO __{column} ({column}) VALUES (%s)', (valeu,))
                        conn.commit()
                        cur.execute(f'SELECT id FROM __{column} WHERE {column}= %s', (valeu,))
                        id= cur.fetchone()
                    if id: id= (id[0])
                    else: id= None
                    column_list.append(f'id_{column}')
                    valeu_list.append(id)
                    continue
                
                column_list.append(column)
                valeu_list.append(valeu)

            column_list.append('fecha_hora')
            valeu_list.append(datetime.now(pytz.timezone('America/Bogota')).strftime("%Y-%m-%d %H:%M"))

            columns_str = ', '.join(column_list)
            placeholders_str = ', '.join(['%s'] * len(valeu_list))
            cur.execute(f'INSERT INTO {table} ({columns_str}) VALUES ({placeholders_str})', valeu_list)
            conn.commit()

            return jsonify({'complete': 'Los datos se han guardado correctamente'}) # MENSAGE DE VALIDACION
        
        except Exception as e:
            error_detalle = traceback.format_exc()
            return jsonify({'error': f'ERROR INESPERADO AL GUARDAR LA INFORMACION DENTRO DE LA BASE DE DATOS \n{str(e)} \n{error_detalle} \n{valeu_list} \n{column_list}'}), 400
    
