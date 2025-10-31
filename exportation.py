import mysql.connector
from flask import Flask, jsonify, request
from datetime import datetime
import pytz
import traceback


## HERRAMIENTAS.
connection = {
    'user': 'root',
    'password': 'VERSER1234',
    'host': '34.31.173.184',
    'database': 'verser-lab',
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
        'id_usuario_salida': 'INT'
    }
    dannos_dic = {
        'numero_de_orden':'BIGINT PRIMARY KEY', 
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
        'numero_de_orden':'BIGINT PRIMARY KEY', 
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


# DEF PARA AGREGAR LOS DATOS DE LOS QUESTIONARIOS A LA BASE DE DATOS MySQL. *** NO GUARDA LAS SALIDAS ***
def guardado_idr():
    data = request.get_json()

    normalized_columns= ('cliente', 'tipo_de_ingresos', 'motivo_de_garantia', 'tipo_de_lente', 'ar', 'estado_de_montura', 
                         'condicion_especial', 'area_responsable', 'lente', 'motivo', 'responsable', 'material', 'usuario')
    
    colums_list=[]
    valeus_list=[]
    with mysql.connector.connect(**connection) as conn:
        cur= conn.cursor(buffered=True)

        table= data.get('tabla')
        # COMPROVANTE DE QUE EL NUMERO DE ORDEN NO SE ENCUENTRA EN LA BASE DE DATOS, EN TAL CASO, MANDAR ERROR.
        numero= data.get('numero_de_orden')
        cur.execute(f'SELECT * FROM {table} WHERE numero_de_orden= %s', (numero,))
        used= cur.fetchone()
        if used:
            return jsonify({'error': 'Este numero de orden ya se encuentra registrado'}), 400 # MANDA ERROR.

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
                    
                    colums_list.append(f'id_{key}')
                    valeus_list.append(id)
                    continue

                colums_list.append(key)
                valeus_list.append(value)

            colums_list.append('fecha')
            valeus_list.append(datetime.now(pytz.timezone('America/Bogota')).strftime("%Y-%m-%d %H:%M"))


            # FUNCION PARA CALCULAR EL PRECIO DE LOS DANNOS
            if table == '_dannos':
                lente= data.get('lente')
                material= data.get('material')
                if lente != 'AO': cantidad= 1
                else: cantidad= 2

                cur.execute('SELECT costo FROM _systema_web_costo_materiales WHERE material=%s', (material,))
                costo_material= cur.fetchone()
                costo_final= costo_material[0] * cantidad

                colums_list.append('costo')
                valeus_list.append(costo_final)
            # *FINAL* DE LA FUNCION QUE CALCULAR EL PRECIO DE LOS DANNOS


            colums= ', '.join(colums_list)
            indicator_list= (['%s'] * len(valeus_list))
            indicator= ', '.join(indicator_list)
            
            cur.execute(f'INSERT INTO {table}({colums}) VALUES({indicator})', valeus_list)
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
            fecha_de_salida = datetime.now(pytz.timezone('America/Bogota')).strftime("%Y-%m-%d %H:%M")
            tardanza = (datetime.strptime(fecha_de_salida, "%Y-%m-%d %H:%M") - fecha_de_ingreso).days
        except Exception as e:
            return jsonify({'error': f'ERROR INESPERADO AL GUARDAR LA INFORMACION DENTRO DE LA BASE DE DATOS, ERROR AL INTENTAR ECONCONTRAR LA TARDANZA ENTRE LAS FECHAS \n{e}'}), 400 # MANDA ERROR.
        
        try:
            cur.execute('SELECT id FROM usuario WHERE usuario = %s', (usuario_salida,))
            id_usuario_salida = cur.fetchone()
            if not id_usuario_salida:
                cur.execute('INSERT IGNORE INTO usuario(usuario) VALUES(%s)', (usuario_salida,))
                conn.commit()
                cur.execute('SELECT id FROM usuario WHERE usuario = %s', (usuario_salida,))
                id_usuario_salida = cur.fetchone()

            if id_usuario_salida: id_usuario_salida = id_usuario_salida[0]
            else: id_usuario_salida = None


            cur.execute('UPDATE _ingresos_y_salidas SET fecha_de_salida = %s, tardanza = %s, id_usuario_salida = %s WHERE numero_de_orden = %s', (fecha_de_salida, int(tardanza), id_usuario_salida, numero))
            conn.commit()
        except Exception as e:
            return jsonify({'error': f'ERROR INESPERADO AL GUARDAR LA INFORMACION DENTRO DE LA BASE DE DATOS \n{e}'}), 400 # MANDA ERROR.
        
        return jsonify({'complete': 'Los datos se han guardado correctamente'}) # MENSAGE DE VALIDACION
    
