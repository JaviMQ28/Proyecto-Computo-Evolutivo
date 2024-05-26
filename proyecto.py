from collections import namedtuple
import math
import sys
import random
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import datetime, time, timedelta

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

def dividir_horas(intervalos):
    hora_inicio_dt = datetime.strptime("8:00:00", "%H:%M:%S")
    hora_fin_dt = datetime.strptime("16:00:00", "%H:%M:%S")

    duracion = hora_fin_dt - hora_inicio_dt
    intervalo_duracion = duracion / intervalos
    periodos = []

    inicio_intervalo = hora_inicio_dt
    for _ in range(intervalos):
        fin_intervalo = inicio_intervalo + intervalo_duracion
        periodos.append((inicio_intervalo.time(), fin_intervalo.time()))
        inicio_intervalo = fin_intervalo

    return periodos
'''
periodos = dividir_horas(5)
print(periodos)
exit(0)
'''

# Función para generar una hora aleatoria
def generar_hora_aleatoria(hora_inicio):    
    hora_fin = "16:00:00"
    hora_inicio_dt = datetime.strptime(hora_inicio, "%H:%M:%S")
    hora_fin_dt = datetime.strptime(hora_fin, "%H:%M:%S")    
    diferencia = hora_fin_dt - hora_inicio_dt
    total_segundos = diferencia.total_seconds()
    segundos_aleatorios = random.randint(0, int(total_segundos))
    hora_aleatoria = (hora_inicio_dt + timedelta(seconds=segundos_aleatorios)).time()

    return str(hora_aleatoria)
'''
hora = generar_hora_aleatoria("08:00:00")
print(hora)
exit(0)
'''

# Genera poblacion de soluciones con representacion de conjuntos de permutaciones
# - solucion[0] = Trayecto del camion
# - solucion[1] = Horario del camion
# - solucion[2] = Hora en que finalizo su trabajo el camion
def genera_poblacion(num_nodos, num_camiones, coordenadas):
    poblacion = []    
    deposito = coordenadas[0]
    i = 0
    while i < 100:      
        coordenadas_agregadas = []  
        solucion = []    
        periodos = dividir_horas(num_camiones)            
        nodos = 1
        camion = 1    
        hora_inicio = "08:00:00"
                          
        while camion <= num_camiones:                                     
            dimension = num_nodos-1
            datos_camion = []
            trayecto = []            
            num_contenedores = 0            
            trayecto.append(deposito)
            coordenadas_agregadas.append(deposito)                
            if dimension > 0:
                num_contenedores = random.randint(1, dimension)
            contenedores = 1
            while contenedores <= num_contenedores:
                coordenada = random.choice(coordenadas)
                if coordenada not in coordenadas_agregadas:                    
                    trayecto.append(coordenada)
                    coordenadas_agregadas.append(coordenada)
                    nodos += 1
                contenedores += 1                                                 
            #print(nodos)      
            if camion == num_camiones and nodos < num_nodos:
                coordenadas_faltantes = [coordenada for coordenada in coordenadas if coordenada not in coordenadas_agregadas]
                for coordenada in coordenadas_faltantes:
                    trayecto.append(coordenada)
                    nodos += 1
            #print(nodos)      
            trayecto.append(deposito) 
            datos_camion.append(trayecto)
            datos_camion.append(periodos[camion-1])
            hora_inicio = generar_hora_aleatoria(hora_inicio)
            datos_camion.append(hora_inicio)
            solucion.append(datos_camion)
            dimension = dimension - contenedores               
            camion += 1                                       
        individuo = Individuo(solucion, 0)
        poblacion.append(individuo)
        i += 1    
    
    return poblacion

def distancia_euclidiana(x, y):
    distancia_x = x[1] - x[0]
    distancia_y = y[1] - y[0]
    distancia = math.sqrt(distancia_x**2 + distancia_y**2)
    return distancia

def evaluar_recorrido(trayecto):
    trafico = 0
    num_residuos = 0
    i = 1
    while i < len(trayecto):
        trafico += distancia_euclidiana(trayecto[i-1][0], trayecto[i][0])
        num_residuos += trayecto[i][1]
        i += 1
    return trafico, num_residuos

'''
trayecto = [[(82, 76), 0], [(98, 14), 12], [(98, 5), 9], [(5, 42), 4], [(82, 76), 0]]
trafico, numR = evaluar_recorrido(trayecto)
print(trafico)
print(numR)
exit(0)
'''

def evaluar_camion(camion, capacidad, penalizacion=1000):    
    total_de_trafico, total_residuos = evaluar_recorrido(camion[0])
    evaluacion = total_de_trafico
    # Evalua la carga total del camion
    if total_residuos > capacidad:
        evaluacion += evaluacion * penalizacion

    # Evalua el tiempo del camion en finalizar
    horario = camion[1]
    hora_de_termino = camion[2]
    hora_dt = time.fromisoformat(hora_de_termino)
    if hora_dt > horario[1]:
        evaluacion += evaluacion * penalizacion

    return evaluacion

def evaluar_individuo(individuo, capacidad):        
    eval_ind = 0
    for i in individuo[0]:
        eval_ind += evaluar_camion(i,capacidad)    
    individuo = individuo._replace(evaluacion=eval_ind)
    return individuo

def evaluar_poblacion(poblacion, capacidad):
    # Evalua a cada individuo de la poblacion
    j = 0
    for i in poblacion:        
        poblacion[j] = evaluar_individuo(i, capacidad)
        j += 1

if __name__ == '__main__':
    ruta_archivo = sys.argv[1]
    numN, numC, capacidad, coordenadas = leer_archivo(ruta_archivo)
    print(f"\nCantidad de nodos: {numN}")
    print(f"Cantidad de camiones: {numC}")
    print(f"Capacidad de cada camión: {capacidad}")
    print(f"Coordenadas: \n{coordenadas}")

    poblacion = genera_poblacion(int(numN), int(numC), coordenadas)
    #print(f'\nPoblación generada: \n{poblacion}')

    evaluar_poblacion(poblacion, int(capacidad))
    print(f'\nEvaluación: \n{poblacion}\n')