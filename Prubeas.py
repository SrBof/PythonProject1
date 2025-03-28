
#int = Entero
#str = texto
#bool = Verdadero/Falso
#float = Decimal

#Variables
#String
variable1 = "Hola como estás"
#int
variables2 = 31
#Bool
variable3 = False

#Funciones - Siempre tienen parentesis al final
print()
#input()

print("Por favor ingrese su nombre")
a = input()
print("Ahora por favor ingrese su edad")
b = input()


print("Tu nombre es: ", a)
print("Y tu edad es: ", b)

#Estructura
# <
# >
# %

print("Dame tu numero y te dire si es par o impar")
numero = int(input())
print(numero)

if numero%2 == 0 and numero != 0:
    print("Tu numero es par")
    resta = 100 - numero
    print("Si quieres que tu numero sea 100, debes sumarle, ", resta)
elif numero%2 == 1:
    print("Tu numero es impar")
elif numero == 0:
    print("Tu numero es 0")


