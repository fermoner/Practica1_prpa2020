from multiprocessing import Process, current_process
from multiprocessing import Manager
from multiprocessing import Semaphore
from random import randint
from math import inf

limInf = 5 #Número mínimo de números que puede generar un productor
limSup = 10 #Número máximo de números que puede generar un productor
NProd = 3 #Número de productores

def productor(pid, almacen, Vacio, Completo):
    dato = 0
    for iter in range(randint(limInf, limSup)): #Cada proceso hace un número aleatorio de iteraciones entre los dos valores.
        dato = randint(dato+1, dato + 100) #El proceso genera un número aleatorio, entre los 99 siguientes al número generado
        print(f"{current_process().name} produce {dato}")
        Vacio[pid].acquire() 
        try:
            almacen[pid] = dato
            print(f"{current_process().name} ha almacenado {dato}")
        finally:
            Completo[pid].release() 
    
    Vacio[pid].acquire()
    try:
        almacen[pid] = -1
    finally:
        Completo[pid].release()
        print(f"{current_process().name} ha terminado")

#Selecciona al menor número obviando negativos.
def indice_min(almacen):
    temp = inf
    for j in range(len(almacen)):
        if (almacen[j]!=-1 and almacen[j]!=-2 and almacen[j] < temp):
            indice = j
            temp = almacen[j]
    return indice


def consumidor(almacen, Vacio, Completo, solucion):
    for S in Completo: #Espera a que todos los productores produzcan.
        S.acquire()
    while any(i != -1 for i in almacen):
        try:
            minimo = indice_min(almacen) #Selecciona el menor y hace lasmodifiaciones
            dato = almacen[minimo]
            almacen[minimo] = -2
            print(f"{current_process().name} ha seleccionado un {dato}")
        finally:
            Vacio[minimo].release()
        solucion.append(dato)
        Completo[minimo].acquire()



def main():
    # Se usa un Manager() para compartir información entre procesos.
    manager = Manager()
    almacen = manager.list()
    solucion = manager.list()
    #Dos listas de semaforos para hacer la sincronizacion
    Completo = [] 
    Vacio = []
    Productores = []
    for pid in range(NProd):
        almacen.append(-2)
        Vacio.append(Semaphore(1))
        Completo.append(Semaphore(0))
        Productores.append(Process(target= productor, name = f"productor {pid}",
                                    args = [pid,almacen,Vacio,Completo]))
    Consumidor = Process(target = consumidor, name = "consumidor",
                         args = [almacen, Vacio, Completo, solucion])
    
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
