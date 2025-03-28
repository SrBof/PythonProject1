a = input()
b = input()
lista = a.split()
nums = b.split()
media = int(lista[1])

#Bubble Sort
n = len(nums)
for i in range(n-1):
    for j in range(n-i-1):
        if nums[j] > nums[j+1]:
            nums[j], nums[j+1] = nums[j+1], nums[j]

pos = int(((n-1)/2) +1) -1
media_lista = int(nums[pos])

if media == media_lista:
    print("0")
elif media > media_lista:
    rest = media - media_lista
    menor = False
    contador = 1
    dulces = 0
    while menor == False:
        if pos == len(nums) - 1:
            menor = True
        elif int(nums[pos]) < media:
                dulces = dulces + (media - int(nums[pos]))
                pos = pos+1
        else:
            menor = True
    print(dulces)
elif media < media_lista:
    aux = 0
    for i in range(pos):
        aux = aux + int(nums[i])
        ta = media * pos
    print(ta - pos)

