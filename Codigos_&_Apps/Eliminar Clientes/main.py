# MENU
# IMPORTACION DE LA FUNCION CREADA
from elimina_clientes import ELIMINAR_CLIENTES

# COMIENZO DEL BUCLE
while True:
    
    # TABLA DE OPCIONES
    print('\n\nSELECCIONE EL ID DE LA ACCION QUE DESEA EJECUTAR\n')
    print(' 1 - Eliminar Cliente')

    # ACCION REALIZADA POR EL USUARIO
    seleccion= input('\n  ELECCION: ')
    if seleccion == '1': ELIMINAR_CLIENTES()
    
    else:
        print('\nOpcion invalida\n')
        input('ENTER')
    
    continue