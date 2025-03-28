import dccortaramas
import funciones
from dccortaramas import DCCortaRamas
from dccortaramas import Bonsai


def menu_de_acciones():
    print("\n"
          "*** Menú de acciones ***\n\n"
          "[1] Visualizar bonsái\n"
          "[2] Modificar Flor\n"
          "[3] Cortar Rama\n"
          "[4] Verificar Simetría\n"
          "[5] Podar Bonsái\n"
          "[6] Salir del programa\n\n"
          "Indique su opción (1, 2, 3, 4, 5, 6):")


def menu_de_inicio():
    print("¡Bienvenido a DCCortaramas!\n\n"
          "*** Menú de Inicio ***\n\n"
          "[1] Cargar bonsái\n"
          "[2] Salir del programa\n\n"
          "Indique su opción (1, 2)"
          )


menu_de_inicio()
accion = 0
while accion != 2:
    accion = input()
    if accion == "1":
        print("Por favor ingrese un nombre de carpeta")
        carpeta = input()
        print("Por favor ingrese un nombre de archivo")
        archivo = input()
        bonsai = Bonsai("arbol", 1, 1, [])
        bonsai.cargar_bonsai_de_archivo(carpeta, archivo)
        dcc = DCCortaRamas()
        print("¡Bienvenido a DCCortaramas!\n"
              "Es hora de convertir tu bonsái en un hermoso bonsái\n\n"
              )
        menu_de_acciones()
        while accion != "6":
            accion = input()
            if accion == "1":
                bonsai.visualizar_bonsai("Vertical", True, False)
                menu_de_acciones()
            elif accion == "2":
                print("Por favor ingrese el identificar del nodo a modificar")
                identificador = input()
                respuesta = dcc.modificar_nodo(bonsai, identificador)
                if respuesta == "No permitido":
                    print("Este nodo no permite edición")
                elif respuesta == "No encontrado":
                    print("No se ha encontrado este nodo, por favor intente de nuevo")
                menu_de_acciones()
            elif accion == "3":
                print("Por favor ingrese el identificador del nodo a cortar")
                identificador = input()
                lista_nodos = funciones.listado_nodos(bonsai.estructura, identificador)
                respuesta = dcc.quitar_nodo(bonsai, identificador)
                if respuesta == "Realizado":
                    print("Se han eliminado los siguientes nodos: ", lista_nodos)
                elif respuesta == "No permitido":
                    print("No está permitido cortar esta rama")
                elif respuesta == "No encontrado":
                    print("No se ha encontrado este nodo, por favor intente de nuevo")
                menu_de_acciones()
            elif accion == "4":
                respuesta = dcc.es_simetrico(bonsai)
                if respuesta:
                    print("El bonsai almacenado actualmente si es simétrico")
                if not respuesta:
                    print("El bonsai almacenado actualmente no es simétrico")
                menu_de_acciones()
            elif accion == "5":
                print("aun no esta hecha")
                menu_de_acciones()
            elif accion == "6":
                print("Muchas gracias por preferirnos, vuelve pronto!")
                exit()
            else:
                print("por favor ingrese una opción válida")
    elif accion == "2":
        print("Gracias por preferirnos!")
        exit()
    else:
        print("Por favor, ingrese una opción válida")
