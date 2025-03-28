from math import trunc

import math

def binario(lista, objetivo=int):
    inicio = 0
    fin = len(lista) - 1
    while inicio <= fin:
        medio = (inicio + fin) // 2  # Encuentra el índice del medio
        if lista[medio] == objetivo:
            while len(lista) > medio:
                if lista[medio] == lista[medio+1]:
                    medio = medio + 1
                else:
                    print(medio+1)
                    return medio+1
            return medio+1  # Retorna la posición donde se encontró el objetivo
        elif lista[medio] < objetivo:
            inicio = medio + 1  # Buscar en la mitad derecha
        else:
            fin = medio - 1  # Buscar en la mitad izquierda

#Variables
list1 = input().split()

goles = int(list1[0])   #numero de goles en el registro
consultas = int(list1[1]) # numero de consultas de cr7
lista_goles = input().split() #lista con los goles por partido
cr_consultas =input().split() #lista con las consultas de cada partido
print(cr_consultas)

lista = [int(i) for i in lista_goles]
lista_pos = []

for i in range(len(cr_consultas)):
    if int(cr_consultas[i]) > int(lista[goles-1]):
        lista_pos.append(goles-1)
    else:
        a = binario(lista, int(cr_consultas[i]))
        if a is not None:
            lista_pos.append(a)
        else:
            contador = 1
            while a is None:
                a = binario(lista, int(cr_consultas[i-contador]))
                contador += 1
            lista_pos.append(a)
print(lista_pos)






