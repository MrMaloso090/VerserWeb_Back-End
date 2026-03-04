#IMPORTACION DEFF .PY
from importation import importar_tabla_mysql
from importation import login_usuarios
from exportation import guardado_idr
from exportation import guardado_s
from exportation import coordinacion_exportacion_general

#IMPORTACION LIBRERIAS
from flask import Flask, jsonify, request
from flask_cors import CORS
import os

# VARIABLE ENVIADA POR LA WEB 
app = Flask(__name__)
CORS(app)  # <--- permite peticiones desde CodePen, GitHub Pages, etc.


#################### FUNCIONES INVOCADAS POR LA WEB PARA LOS --SELECT-- ####################
#TOMA DE DATOS PARA EL SELECT DE CLIENTES.
@app.route("/peticion_clientes", methods=["GET"])
def clientes():
    return importar_tabla_mysql('_systema_web_clientes')

#TOMA DE DATOS PARA EL SELECT DE RESPONSABLE DE DANNOS.
@app.route("/peticion_dannos_responsables", methods=["GET"])
def dannos_responsables():
    return importar_tabla_mysql('_systema_web_dannos_responsables')


#################### FUNCIONE QUE REALIZA LA VALIDACION DEL LOGIN DE LOS USUARIOS ####################
@app.route("/login_usuario", methods=["POST"])
def inicio_de_sesion():
    return login_usuarios()


#################### FUNCIONES INVOCADAS POR LA WEB PARA -- GUARDAR LO RECOLECTADO DEL CUESTIONARIO EN LA BASE DE DATOS ####################
# ESTA FUNCION GUARDA LOS DATOS DE: INGRESOS, DANNOS Y REPROCESOS.
@app.route("/guardado_en_DBs_IDR", methods=["POST"])
def guardado_IDR():
    return guardado_idr()

# ESTA FUNCION GUARDA LOS DATOS DE: SALIDAS.
@app.route("/guardado_en_DB_S", methods=["POST"])
def guardado_S():
    return guardado_s()

# ESTA FUNCION GUARDA LOS DATOS DE: SALIDAS.
@app.route("/guardado_coordinacion_general", methods=["POST"])
def Coordinacion_exportacion_general():
    return coordinacion_exportacion_general()



#################### INVOCACION ####################
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

