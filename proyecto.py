from collections import namedtuple
import sys
import random
import numpy as np
import matplotlib.pyplot as plt
import time

# Nueva tupla de tipo Individuo que tiene su solucion y la evaluacion de la solucion
Individuo = namedtuple('Individuo', ['solucion', 'evaluacion'])

def leer_archivo(ruta_archivo):    
    coordenadas = []
    num_camiones = 0
    num_nodos = 0
    capacidad_camion = 0        

    with open(ruta_archivo, 'r') as archivo:
        # Leer todas las líneas en una lista
        lineas = archivo.readlines()
    
    with open(ruta_archivo, 'r') as archivo:        
        lim_inf_coordenadas = 0
        lim_sup_coordenadas = 0
        lim_inf_residuos = 0
        lim_sup_residuos = 0
        num_linea = 0
        
        for linea in archivo:
            num_linea += 1
            linea = linea.strip()

            # Recuperamos la cantidad de camiones
            if linea.startswith('NAME'):
                num = linea.find('k')
                num_camiones = linea[num+1:]
                #print(f'Cantidad de camiones = {num_camiones}')
            # Recuperamos la capacidad de cada camion
            elif linea.startswith('CAPACITY'):
                _, _, capacidad_camion = linea.split()
                #print(f'Capacidad máxima de cada camión = {capacidad_camion}')
            # Recuperamos la cantidad de nodos
            elif linea.startswith('DIMENSION'):
                _, _, num_nodos = linea.split()
                #print(f'Capacidad máxima de cada camión = {capacidad_camion}')
            # Guardamos el numero de linea donde comienza una seccion del archivo
            elif linea.startswith('NODE_COORD_SECTION'):
                lim_inf_coordenadas = num_linea
            # Guardamos el numero de linea donde termina una seccion del archivo y comienza otra seccion del archivo
            elif linea.startswith('DEMAND_SECTION'):
                lim_sup_coordenadas = num_linea - 2
                lim_inf_residuos = num_linea
            # Guardamos el numero de linea donde termina la otra seccion del archivo
            elif linea.startswith('DEPOT_SECTION'):                
                lim_sup_residuos = num_linea - 2 
            else:
                continue            
    
    # Filtrar las líneas deseadas
    lineas_deseadas = [linea for i, linea in enumerate(lineas) if i >= lim_inf_coordenadas and i <= lim_sup_coordenadas]
    # Recuperar coordenadas
    for linea in lineas_deseadas:
        _, x, y = linea.split()
        coordenadas.append([(int(x),int(y)), 0])
    #print(f'Ubicación de los contenedores, sin cantidad de residuos acumulados : \n {coordenadas}')

    # Filtrar las líneas deseadas
    lineas_deseadas = [linea for i, linea in enumerate(lineas) if i >= lim_inf_residuos and i <= lim_sup_residuos]
    num_linea = 0
    # Recuperar cantidad de residuos acumulados de cada contenedor
    for linea in lineas_deseadas:
        _, residuos = linea.split()
        coordenadas[num_linea][1] = int(residuos)
        num_linea += 1
    #print(f'Ubicación de los contenedores, con cantidad de residuos acumulados : \n {coordenadas}')

    return num_nodos, num_camiones, capacidad_camion, coordenadas

if __name__ == '__main__':
    ruta_archivo = sys.argv[1]
    numN, numC, capacidad, coordenadas = leer_archivo(ruta_archivo)
    print(f"\nCantidad de nodos: {numN}")
    print(f"Cantidad de camiones: {numC}")
    print(f"Capacidad de cada camión: {capacidad}")
    print(f"Coordenadas: \n{coordenadas}\n")