from copy import deepcopy


#Funcion que recibe la esctrucura del bonsai y un identificador de nodo.
#En caso de encontrar la posición de ese nodo en el bonsai,retorna su posición.
#En caso de no encontrarlo retorna -1
def encontrar_nodo(estructura: list, identificador: str) -> int:
    salida_default = -1
    for posicion in range(len(estructura)):
        comparador = str(estructura[posicion][0])
        if comparador == identificador:
            return posicion
    return salida_default


#Función que recibe la estructura de un bonsai y un identificador de nodo.
#Retorna la posición del nodo padre del identificador dado.
#Esta función asume que el nodo tiene padre, se debe hacer la validación de los datos antes de llamarla
def encontrar_nodo_padre(estructura: list, identificador: str) -> list:
    for posicion in range(len(estructura)):
        if estructura[posicion][3][0] == identificador:
            lista_posicion = [posicion, 3, 0]
            return lista_posicion
        if estructura[posicion][3][1] == identificador:
            lista_posicion = [posicion, 3, 1]
            return lista_posicion
    return []


#Función que recibe, la estructura del bonsai y la posición de un nodo.
#Chequea si ese nodo es editable, si es editable, retorna True, si no, retorna False
def editable(estructura: list, id: int) -> bool:
    if estructura[id][2]:
        return True
    else:
        return False


#Función que recibe, la estructura del bonsai, y la posición de un nodo
#Si ese nodo tiene flor, la elimina, si ese nodo no tiene flor, se la agrega
#No retorna nada
def edicion_flor(estructura: list, id: int):
    if editable(estructura, id):
        if estructura[id][1]:
            estructura[id][1] = False
            print("Se ha removido la flor")
        elif not estructura[id][1]:
            estructura[id][1] = True
            print("Se ha agregado una flor")


#Función que recibe, la estructura de un bonsai, y el identificador de un nodo
# Retorna una lista que contiene los identificadores del nodo padre con todos sus hijos.
def listado_nodos(estructura: list, identificador: str) -> list:
    id = encontrar_nodo(estructura, identificador)
    lista_nodos = [estructura[id][0]]
    contador = 0
    while len(lista_nodos) > contador:
        id = encontrar_nodo(estructura, lista_nodos[contador])
        if id != -1:
            hijo_1 = estructura[id][3][0]
            hijo_2 = estructura[id][3][1]
            if hijo_1 != "0":
                lista_nodos.append(hijo_1)
            if hijo_2 != "0":
                lista_nodos.append(hijo_2)
        contador = contador + 1
    return lista_nodos


#Función que recibe una "Rama" (lista de nodos) del bonsai,
#Retorna un booleano el cual determina si la "rama" completa es editable o no
def rama_editable(rama: list, estructura1: list) -> bool:
    contador = 0
    print(len(rama))
    for posicion in range(len(rama)):
        identificador = rama[posicion]
        posicion = encontrar_nodo(estructura1, identificador)
        if estructura1[posicion][2]:
            contador = contador + 1
    if contador == len(rama):
        return True
    else:
        return False


#Función que recibe la estructura de un bonsai, y 2 identificadores de nodos a comparar
#Retorna un booleano el cual determina si los nodos ingresados son iguales o no
def comparador_nodos(estructura, identificador_izq, identificador_der):
    id_izq = encontrar_nodo(estructura, identificador_izq)
    id_der = encontrar_nodo(estructura, identificador_der)

    if estructura[id_izq][1] != estructura[id_der][1]:
        return False

    nodo_izq_izq = estructura[id_izq][3][0]
    nodo_der_der = estructura[id_der][3][1]
    nodo_izq_der = estructura[id_izq][3][1]
    nodo_der_izq = estructura[id_der][3][0]

    if (nodo_izq_izq == "0" and nodo_der_der != "0") or (nodo_izq_izq != "0" and nodo_der_der == "0"):
        return False
    if (nodo_izq_der == "0" and nodo_der_izq != "0") or (nodo_izq_der != "0" and nodo_der_izq == "0"):
        return False

    return True


#Función recursiva que recibe la estructura de un bonsai, y 2 nodos que comparten padre
#La función verifica si la estructura del bonsai es simétrico.
def simetria(estructura, hijo_izq, hijo_der) -> bool:
    if hijo_izq == "0" and hijo_der == "0":
        return True
    if hijo_izq == "0" or hijo_der == "0":
        return False
    if not comparador_nodos(estructura, hijo_izq, hijo_der):
        return False
    id_izq = encontrar_nodo(estructura, hijo_izq)
    id_der = encontrar_nodo(estructura, hijo_der)

    nodo_izq_izq = estructura[id_izq][3][0]
    nodo_izq_der = estructura[id_izq][3][1]
    nodo_der_der = estructura[id_der][3][1]
    nodo_der_izq = estructura[id_der][3][0]
    #La recursividad se aplica para los nodos que hacen de "espejo", ya que estos son los que queremos comparar
    # y verificar si comparten estructura.
    return simetria(estructura, nodo_izq_izq, nodo_der_der) and simetria(estructura, nodo_izq_der, nodo_der_izq)


def simetria_emparejar(bonsai_copia, hijo_izq, hijo_der, lista_movimientos) -> list:
    estructura = bonsai_copia.estructura
    lista_aux = []
    if hijo_izq == "0" or hijo_der == "0":
        if hijo_izq != "0":
            if rama_editable(hijo_izq, estructura):
                entrada = ["Quitar nodo", hijo_izq]
            lista_movimientos.append(entrada)
        else:
            if rama_editable(hijo_der, estructura):
                entrada = ["Quitar nodo", hijo_der]
            lista_movimientos.append(entrada)
    id_izq = encontrar_nodo(estructura, hijo_izq)
    id_der = encontrar_nodo(estructura, hijo_der)
    if estructura[id_izq][1] != estructura[id_der][1]:
        if editable(estructura, id_izq):
            edicion_flor(estructura, id_izq)
            lista_aux.append("Modificar flor")
            lista_aux.append(id_izq)
            lista_movimientos.append(lista_movimientos)
        elif editable(estructura, id_der):
            editable(estructura, id_der)
            lista_aux.append("modificar flor")
            lista_aux.append(hijo_izq)
            lista_movimientos.append(lista_movimientos)
    return lista_movimientos
