from multiprocessing import Process, current_process
from multiprocessing import Semaphore
from multiprocessing import Manager
from random import randint
from math import inf

limInf = 5 #Número mínimo de números que puede generar un productor
limSup = 15 #Número máximo de números que puede generar un productor
NProd = 5  #Número de productores
NBuffer = 3 #Tamaño del buffer en el que los productores pueden alamcenar losdatos

def productor(pid, almacen, NoLLeno, Completo):
    dato = 0
    for iter in range(randint(limInf, limSup)): #Cada proceso hace un número aleatorio de iteraciones entre los dos valores.
        dato = randint(dato+1, dato + 100) #El proceso genera un número aleatorio, entre los 99 siguientes al número generado
        print(f"{current_process().name} produce {dato}")
        NoLLeno[pid].acquire() 
        try:
            if almacen[pid][0] == -2:
                almacen[pid].pop(0)
            almacen[pid].append(dato)
            print(f"{current_process().name} ha almacenado {dato}")
        finally:
            Completo[pid].release() 
    
    NoLLeno[pid].acquire() 
    try:
        almacen[pid].append(-1)
    finally:
        Completo[pid].release() 
        print(f"{current_process().name} ha terminado")


#Selecciona al menor número obviando negativos.
def indice_min(almacen):
    indice = None
    temp = inf
    for j in range(len(almacen)):
        if (almacen[j][0]!=-1 and almacen[j][0]!=-2 and almacen[j][0] < temp):
            indice = j
            temp = almacen[j][0]
    return indice


def consumidor(almacen, NoLLeno, Completo, solucion):
    for S in Completo: #Espera a que todos los productores produzcan.
        S.acquire()
    while any(i[0] != -1 for i in almacen):
        try:
            minimo = indice_min(almacen) #Selecciona el menor y hace las modifiaciones
            dato = almacen[minimo].pop(0)
            if not almacen[minimo]:
                almacen[minimo].append(-2)
            print(f"{current_process().name} ha seleccionado un {dato}")
        finally:
            NoLLeno[minimo].release()
            solucion.append(dato)
            Completo[minimo].acquire()


def main():
    manager = Manager() #Se usa un manager para compartir información entre procesos.
    almacen = manager.list()
    solucion = manager.list()
    #Dos listas de semaforos para hacer la sincronizacion
    Completo = []
    NoLLeno = []
    Productores = []
    for pid in range(NProd):
        almacen.append(manager.list())
        almacen[pid].append(-2) #Cuando se vacia una lista se coloca un -2 para ser coherente con el enunciado
        NoLLeno.append(Semaphore(NBuffer))
        Completo.append(Semaphore(0))
        Productores.append(Process(target= productor, name = f"productor {pid}",
                                    args = [pid,almacen,NoLLeno,Completo]))
    Consumidor = Process(target = consumidor, name = "consumidor",
                         args = [almacen, NoLLeno, Completo, solucion])
    
    for p in Productores:
        p.start()
    Consumidor.start()

    for p in Productores:
        p.join()
    Consumidor.join()

    print(f"La lista ordenada es de tamaño {len(solucion)}")
    print(solucion)
    return solucion[:] #Se indexa para que devuelva un objeto tipo lista.

if __name__ == '__main__':
    main()
