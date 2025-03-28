import copy
import os
from os.path import split
from pathlib import Path
import utilidades
import funciones
from copy import deepcopy

#Error es crasheo
#Fail es retorno incorrecto



class Bonsai:
    def __init__(
        self,
        identificador: str,
        costo_corte: int,
        costo_flor: int,
        estructura: list
    ) -> None:
        self.identificador = identificador
        self.costo_corte = costo_corte
        self.costo_flor = costo_flor
        self.estructura = estructura

    def cargar_bonsai_de_archivo(self, carpeta: str, archivo: str):
        path = os.path.join("data",carpeta, archivo)
        file = open(path, "r", encoding="UTF-8")

        lineas = file.readlines()
        file.close()
        lista_estructura = []
        for linea in lineas:
            identificador, flor, editable, nodos = linea.strip().split(",")
            nodos = nodos.split(";")
            if flor == "T":
                flor = True
            elif flor == "F":
                flor = False
            if editable == "T":
                editable = True
            elif editable == "F":
                editable = False
            lista_base = [identificador, bool(flor), bool(editable), list(nodos)]
            lista_estructura.append(lista_base)
        self.estructura = lista_estructura

    def visualizar_bonsai(self, orientacion: str, emojis: bool, guardar_archivo: bool) -> None:
        if guardar_archivo:
            lineas = utilidades.visualizar_bonsai(self.estructura, orientacion, emojis, guardar_archivo)
            identificador = self.identificador + ".txt"
            path = os.path.join("visualizaciones", identificador)
            file = open(path, "w", encoding="UTF-8")
            file.writelines(lineas)
            file.close()
        else:
            utilidades.visualizar_bonsai(self.estructura, orientacion, emojis, guardar_archivo)
#py -m unittest -v -b tests_publicos.test_00_cargar_bonsai_de_archivo

class DCCortaRamas:
    def modificar_nodo(self, bonsai: Bonsai, identificador: str) -> str:
        estructura = bonsai.estructura
        mensaje = "No encontrado"
        id = funciones.encontrar_nodo(estructura, identificador)
        #Se pone id distinto a -1 ya que el ID no puede ser negativo
        if id != -1:
            if funciones.editable(estructura, id):
                funciones.edicion_flor(estructura, id)
                return  "Realizado"
            else:
                return "No permitido"
        else:
            mensaje = "No encontrado"
        return mensaje

#py -m unittest -v -b tests_publicos.test_02_modificar_nodo
    def quitar_nodo(self, bonsai: Bonsai, identificador: str) -> str:
        estructura = bonsai.estructura
        print(estructura)
        id = funciones.encontrar_nodo(estructura, identificador)
        if id != -1:
            lista_nodos = funciones.listado_nodos(estructura, identificador)
            rama_editable = funciones.rama_editable(lista_nodos, estructura)
            if rama_editable:
                nueva_estructura = []
                for posicion in range(len(estructura)):
                    if estructura[posicion][0] not in lista_nodos:
                        nueva_estructura.append(estructura[posicion])
                posicion = funciones.encontrar_nodo_padre(estructura, identificador)
                if len(posicion) > 1:
                    nueva_estructura[posicion[0]][posicion[1]][posicion[2]] = "0"
                bonsai.estructura = nueva_estructura
                return "Realizado"
            else:
                return "No permitido"
        else:
            return "No encontrado"


    def es_simetrico(self, bonsai: Bonsai) -> bool:
        estructura = bonsai.estructura
        id = funciones.encontrar_nodo(estructura, "1")
        hijo_izq = estructura[id][3][0]
        hijo_der = estructura[id][3][1]
        #Si los hijos de la raíz son 0, el bonsai es simetrico
        if hijo_izq == "0" and hijo_der == "0":
            return True
        #Si 1 de los hijos es 0 y el otro no, ya no es simetrico
        if hijo_izq == "0" or hijo_der == "0":
            return False
        simetria = funciones.simetria(estructura, hijo_izq, hijo_der)
        return simetria

    def emparejar_bonsai(self, bonsai: Bonsai) -> list:
        bonsai_copia = deepcopy(bonsai)  # Copia para no modificar el original
        estructura = bonsai_copia.estructura
        if self.es_simetrico(bonsai_copia):
            return [True, []]
        lista_movimientos = []

        id_raiz = funciones.encontrar_nodo(estructura, "1")  # Encontrar la raíz
        hijo_izq = estructura[id_raiz][3][0]
        hijo_der = estructura[id_raiz][3][1]

        if not self.es_simetrico(bonsai_copia):  # Mientras no sea simétrico
            lista_movimientos.append(funciones.simetria_emparejar(bonsai_copia, hijo_izq, hijo_der))
        else:
            lista_movimientos = [True,[]]
        return lista_movimientos

    def emparejar_bonsai_ahorro(self, bonsai: Bonsai) -> list:
        pass

    def comprobar_solucion(self, bonsai: Bonsai, instrucciones: list) -> list:
        pass

