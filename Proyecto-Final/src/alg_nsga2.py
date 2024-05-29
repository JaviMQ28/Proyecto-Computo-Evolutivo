from collections import namedtuple
import csv
import math
import os
import sys
import random
import numpy as np
import matplotlib.pyplot as plt
from time import perf_counter
from datetime import datetime, time, timedelta
import tkinter

import pandas as pd

# Nueva tupla de tipo Individuo que tiene su solucion y la evaluacion de la solucion
Individuo = namedtuple('Individuo', ['solucion', 'evaluacion', 'evaluacion_trayecto', 'evaluacion_carga', 'evaluacion_tiempo', 'dominacion', 'distancia'])

# Para la graficas
y_mejor = []
y_mejor_actual = []
y_promedio = []
y_peor = [] 
y_peor_actual = []
trayectos_soluciones = []
cargas_soluciones = []
tiempos_soluciones = []


# Lectura de un archivo .txt para recuperar datos para el problema
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
            # Recuperamos la capacidad de cada camion
            elif linea.startswith('CAPACITY'):
                _, _, capacidad_camion = linea.split()
            # Recuperamos la cantidad de nodos
            elif linea.startswith('DIMENSION'):
                _, _, num_nodos = linea.split()
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

    # Filtrar las líneas deseadas
    lineas_deseadas = [linea for i, linea in enumerate(lineas) if i >= lim_inf_residuos and i <= lim_sup_residuos]
    num_linea = 0
    # Recuperar cantidad de residuos acumulados de cada contenedor
    for linea in lineas_deseadas:
        _, residuos = linea.split()
        coordenadas[num_linea][1] = int(residuos)
        num_linea += 1

    return num_nodos, num_camiones, capacidad_camion, coordenadas

# Divide un periodo de tiempo en periodos de tiempo iguales
def dividir_horas(intervalos, horario):
    hora_inicio_dt = datetime.strptime(horario[0], "%H:%M:%S")
    hora_fin_dt = datetime.strptime(horario[1], "%H:%M:%S")

    duracion = hora_fin_dt - hora_inicio_dt
    intervalo_duracion = duracion / intervalos
    periodos = []

    inicio_intervalo = hora_inicio_dt
    for _ in range(intervalos):
        fin_intervalo = inicio_intervalo + intervalo_duracion
        periodos.append((inicio_intervalo.time(), fin_intervalo.time()))
        inicio_intervalo = fin_intervalo

    return periodos

# Función para generar una hora aleatoria
def generar_hora_aleatoria(horario, hora_final):         
    hora_inicio_dt = datetime.strptime(str(horario[0]).split(".")[0], "%H:%M:%S")
    hora_fin_dt = datetime.strptime(hora_final, "%H:%M:%S")    
    diferencia = hora_fin_dt - hora_inicio_dt
    total_segundos = diferencia.total_seconds()
    segundos_aleatorios = random.randint(0, int(total_segundos))
    hora_aleatoria = (hora_inicio_dt + timedelta(seconds=segundos_aleatorios)).time()

    return str(hora_aleatoria)

# Obtiene la distancia euclidiana, que representara el trafico que tiene una calle
def distancia_euclidiana(x, y):
    distancia_x = x[1] - x[0]
    distancia_y = y[1] - y[0]
    distancia = math.sqrt(distancia_x**2 + distancia_y**2)
    return distancia

# Evalua el recorrido realizado por un camion, de acuerdo al trafico que hubo y la carga de residuos que se recogieron
def evaluar_recorrido(trayecto):
    trafico = 0
    num_residuos = 0
    i = 1
    while i < len(trayecto):
        trafico += distancia_euclidiana(trayecto[i-1][0], trayecto[i][0])
        num_residuos += trayecto[i][1]
        i += 1
    return trafico, num_residuos

# Evalua el trabajo de un camion, con una capacidad de carga limitada, de acuerdo al recorrido que hizo y el tiempo que le llevo en hacerlo
def evaluar_camion(camion, capacidad, penalizacion=1000):    
    total_de_trafico, total_residuos = evaluar_recorrido(camion[0])
    evaluacion = total_de_trafico
    evaluacion_trafico = total_de_trafico
    evaluacion_carga = total_residuos
    # Evalua la carga total del camion
    if total_residuos > capacidad:
        evaluacion += evaluacion * penalizacion
        evaluacion_carga += evaluacion_carga * penalizacion

    # Evalua el tiempo del camion en finalizar
    horario = camion[1]
    hora_de_termino = camion[2]
    hora_dt = time.fromisoformat(hora_de_termino)
    evaluacion_tiempo = 1
    if hora_dt > horario[1]:
        evaluacion += evaluacion * penalizacion
        evaluacion_tiempo += evaluacion_tiempo * penalizacion

    return evaluacion, evaluacion_trafico, evaluacion_carga, evaluacion_tiempo

# Evalua una solucion, que representa los recorridos realizados por la cantidad de camiones que se definio con sus horarios establecidos de cada uno
def evaluar_individuo(individuo, capacidad):        
    eval_ind = 0
    eval_trafico = 0
    eval_carga = 0
    eval_tiempo = 0
    
    for i in individuo[0]:
        eval, eval_Tr, eval_C, eval_Ti = evaluar_camion(i,capacidad)    
        eval_ind += eval
        eval_trafico += eval_Tr
        eval_carga += eval_C
        eval_tiempo += eval_Ti

    individuo = individuo._replace(evaluacion=eval_ind, evaluacion_trayecto=eval_trafico, evaluacion_carga=eval_carga, evaluacion_tiempo=eval_tiempo)
    return individuo

# Evalua a una poblacion de soluciones
def evaluar_poblacion(poblacion, capacidad):
    # Evalua a cada individuo de la poblacion
    j = 0
    for i in poblacion:        
        poblacion[j] = evaluar_individuo(i, capacidad)
        j += 1

# Genera una poblacion de soluciones con representacion de conjuntos de permutaciones
# - solucion[0] = Trayecto del camion
# - solucion[1] = Horario del camion
# - solucion[2] = Hora en que finalizo su trabajo el camion
def genera_poblacion(num_nodos, num_camiones, coordenadas, horario):
    poblacion = []    
    deposito = coordenadas[0]
    i = 0
    while i < 100:      
        coordenadas_agregadas = []  
        solucion = []    
        periodos = dividir_horas(num_camiones, horario)            
        nodos = 1
        camion = 1                              
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
            if camion == num_camiones and nodos < num_nodos:
                coordenadas_faltantes = [coordenada for coordenada in coordenadas if coordenada not in coordenadas_agregadas]
                for coordenada in coordenadas_faltantes:
                    trayecto.append(coordenada)
                    nodos += 1
            trayecto.append(deposito) 
            datos_camion.append(trayecto)
            datos_camion.append(periodos[camion-1])
            hora_que_finalizo = generar_hora_aleatoria(periodos[camion-1], horario[1])
            datos_camion.append(hora_que_finalizo)
            solucion.append(datos_camion)
            dimension = dimension - contenedores               
            camion += 1                                       
        individuo = Individuo(solucion, 0, 0, 0, 0, [0,None], 0)
        poblacion.append(individuo)
        i += 1    
    
    return poblacion

# Regresa dos individuos de la poblacion que seran los padres
def seleccion_por_torneo(poblacion, capacidad):
    seleccionados = []
    k = 0    
    # Seleccionamos k individuos de la poblacion
    while k < 10:
        individuo = random.choice(poblacion)
        if individuo not in seleccionados:                    
            seleccionados.append(individuo)
        k += 1
    seleccionados = sorted(seleccionados, key=lambda individuo: evaluar_individuo(individuo, capacidad).evaluacion)    
    # Obtenemos al mejor de los seleccionados
    mejor_de_seleccionados_1 = seleccionados[0]

    seleccionados = []
    k = 0    
    # Seleccionamos otros k individuos de la poblacion
    while k < 10:
        individuo = random.choice(poblacion)
        if individuo not in seleccionados:                    
            seleccionados.append(individuo)
        k += 1
    seleccionados = sorted(seleccionados, key=lambda individuo: evaluar_individuo(individuo, capacidad).evaluacion)    
    # Obtenemos al mejor de los seleccionados
    mejor_de_seleccionados_2 = seleccionados[0]
    
    return poblacion.index(mejor_de_seleccionados_1), poblacion.index(mejor_de_seleccionados_2)

# Realiza el cruce para permutaciones, con probabilidad pc => [0.6-0.9], 
# para los horarios de los hijos uno tendra el horario del primer padre y el otro del segundo,
# para los trayectos de cada camion de los hijos seran de diferentes tamaños al de los padres
def cruza_de_permutaciones(sol1, sol2, pc):    
    trayecto_de_sol1 = []
    trayecto_de_sol2 = []
    sol_hijo1 = []
    sol_hijo2 = []
    trayecto_de_h1 = []
    trayecto_de_h2 = []    
    
    # Recupera el trayecto de los camiones a los contenedores, sin contar al deposito, de la primera solucion
    for camion in sol1:
        trayecto = camion[0]
        deposito = trayecto[0]
        contenedor = 1
        while trayecto[contenedor] != deposito:
            trayecto_de_sol1.append(trayecto[contenedor])
            contenedor += 1
    # Recupera el trayecto de los camiones a los contenedores, sin contar al deposito, de la segunda solucion
    for camion in sol2:
        trayecto = camion[0]
        deposito = trayecto[0]
        contenedor = 1
        while trayecto[contenedor] != deposito:
            trayecto_de_sol2.append(trayecto[contenedor])
            contenedor += 1

    tamanio = len(trayecto_de_sol1)
    indice_comienzo = random.randrange(0, tamanio)
    indice_final = random.randrange(indice_comienzo, tamanio)
    indices_no_agregados = []
    ind = 0
    # Se agregan unas coordenadas, el hijo 1 del padre A y el hijo 2 del padre B
    while ind < tamanio:
        if ind >= indice_comienzo and ind <= indice_final:
            if np.random.rand() <= pc:
                trayecto_de_h1.append(trayecto_de_sol1[ind])
                trayecto_de_h2.append(trayecto_de_sol2[ind])
            else:
                trayecto_de_h1.append(None)
                trayecto_de_h2.append(None)
                indices_no_agregados.append(ind)
        else:            
            trayecto_de_h1.append(None)
            trayecto_de_h2.append(None)         
            indices_no_agregados.append(ind)   
        ind += 1    
    # Se agregan las coordenadas faltantes de los padres, el hijo 1 del padre B y el hijo 2 del padre A
    for indice in indices_no_agregados:
        if trayecto_de_h1[indice] == None and trayecto_de_h2[indice] == None:
            ind = 0
            while ind < len(trayecto_de_sol1):
                if trayecto_de_sol2[ind] not in trayecto_de_h1:
                    trayecto_de_h1[indice] = trayecto_de_sol2[ind]
                ind += 1
            ind = 0
            while ind < len(trayecto_de_sol1):
                if trayecto_de_sol1[ind] not in trayecto_de_h2:
                    trayecto_de_h2[indice] = trayecto_de_sol1[ind]            
                ind += 1            

    # Se crea la primer solucion de acuerdo a la definicion establecida y del trayecto que se realizo anteriormente para el hijo 1
    num_camiones = len(sol1)
    num_nodos = len(trayecto_de_h1) + 1
    sol_hijo1 = []
    camion = 1
    nodos = 1
    while camion <= num_camiones:
        dimension = len(trayecto_de_h1)-1
        datos_camion = []
        trayecto_h1 = []
        trayecto_h1.append(deposito)              
        if dimension > 0:
            num_contenedores = random.randint(1, dimension)
        contenedores = 1
        while contenedores < num_contenedores:
            contenedor = trayecto_de_h1[0]
            trayecto_h1.append(contenedor)            
            trayecto_de_h1.remove(contenedor)
            contenedores += 1                                                         
        if camion == num_camiones and nodos < num_nodos:
            contenedores_faltantes = [coordenada for coordenada in trayecto_de_h1 if coordenada not in trayecto_h1]
            for contenedor in contenedores_faltantes:
                trayecto_h1.append(contenedor)
                trayecto_de_h1.remove(contenedor)
                nodos += 1
        
        trayecto_h1.append(deposito) 
        datos_camion.append(trayecto_h1)
        datos_camion.append(sol1[camion-1][1])
        hora_que_finalizo = generar_hora_aleatoria(sol1[camion-1][1], horario[1])
        datos_camion.append(hora_que_finalizo)
        sol_hijo1.append(datos_camion)
        dimension = dimension - contenedores               
        camion += 1  
    ind1 = Individuo(sol_hijo1, 0, 0, 0, 0, [0,None], 0)

    # Se crea la segunda solucion de acuerdo a la definicion establecida y del trayecto que se realizo anteriormente para el hijo 2
    num_camiones = len(sol2)
    num_nodos = len(trayecto_de_h2) + 1
    sol_hijo2 = []
    camion = 1
    nodos = 1
    while camion <= num_camiones:
        dimension = len(trayecto_de_h2)-1
        datos_camion = []
        trayecto_h2 = []
        trayecto_h2.append(deposito)              
        if dimension > 0:
            num_contenedores = random.randint(1, dimension)
        contenedores = 1
        while contenedores < num_contenedores:
            contenedor = trayecto_de_h2[0]
            trayecto_h2.append(contenedor)            
            trayecto_de_h2.remove(contenedor)
            contenedores += 1                                                 
        
        if camion == num_camiones and nodos < num_nodos:
            contenedores_faltantes = [coordenada for coordenada in trayecto_de_h2 if coordenada not in trayecto_h2]
            for contenedor in contenedores_faltantes:
                trayecto_h2.append(contenedor)
                trayecto_de_h2.remove(contenedor)
                nodos += 1        
        trayecto_h2.append(deposito) 
        datos_camion.append(trayecto_h2)
        datos_camion.append(sol2[camion-1][1])
        hora_que_finalizo = generar_hora_aleatoria(sol2[camion-1][1], horario[1])
        datos_camion.append(hora_que_finalizo)
        sol_hijo2.append(datos_camion)
        dimension = dimension - contenedores               
        camion += 1  
    ind2 = Individuo(sol_hijo2, 0, 0, 0, 0, [0,None], 0)

    return ind1, ind2

# Realiza la mutacion de un individuo, con probabilidad pc => [0.01-0.1]
def mutacion(solucion, pm):
    trayecto_de_sol = []
    # Recupera el trayecto de los camiones a los contenedores, sin contar al deposito
    for camion in solucion:
        trayecto = camion[0]
        deposito = trayecto[0]
        contenedor = 1
        while trayecto[contenedor] != deposito:
            trayecto_de_sol.append(trayecto[contenedor])
            contenedor += 1
    
    # Se intercambia la ubicacion de dos contenedores, para establecer un recorrido diferente
    i = 0
    while i < len(trayecto_de_sol):
        if np.random.rand() <= pm:
            temp = trayecto_de_sol[i]
            pos_random = random.randint(i, len(trayecto_de_sol)-1)
            trayecto_de_sol[i] = trayecto_de_sol[pos_random]
            trayecto_de_sol[pos_random] = temp                         
        i += 1
    
    # Se actualizan los nuevos recorridos de cada camion
    deposito = solucion[0][0][0]
    camion = 0
    ind = 0
    while camion < len(solucion):
        i = 0
        while i < len(solucion[camion][0]):              
            if solucion[camion][0][i] != deposito:
                solucion[camion][0][i] = trayecto_de_sol[ind]
                ind += 1
            i += 1     
        camion += 1   
    mut = Individuo(solucion, 0, 0, 0, 0, [0,None], 0)
    
    return mut

# Elimina las sublistas vacias de una lista
def limpiar_lista(lista):    
    lista = [sublista for sublista in lista if sublista]
    return lista 

# Obtiene el promedio de una poblacion de acuerdo a la evaluacion de cada individuo
def promedio(poblacion):
    suma_aptitudes = 0
    for i in poblacion:
        suma_aptitudes += i.evaluacion
    y_promedio.append(suma_aptitudes/len(poblacion))

# Ordena la poblacion de acuerdo al ordenamiento no determinado, non-determinated sorting, regresando una lista de sublistas de indices de las 
# ubicaciones de los individuos, de donde deberan de estar ubicados
# A(x1|y1) domina a B(x2|y2) cuando:
# (x1 ≤ x2 y y1 ≤ y2) y (x1 < x2 o y1 < y2)
def ordenamiento_no_determinado(poblacion):
    # Se calcula lo dominacion de cada individuo
    i = 0    
    while i < len(poblacion):     
        dominados = []   
        j = 0
        while j < len(poblacion):              
            if poblacion[i] != poblacion[j]:
                if (poblacion[i].evaluacion_trayecto >= poblacion[j].evaluacion_trayecto and poblacion[i].evaluacion_carga >= poblacion[j].evaluacion_carga and poblacion[i].evaluacion_tiempo >= poblacion[j].evaluacion_tiempo) and (poblacion[i].evaluacion_trayecto > poblacion[j].evaluacion_trayecto or poblacion[i].evaluacion_carga > poblacion[j].evaluacion_carga or poblacion[i].evaluacion_tiempo > poblacion[j].evaluacion_tiempo):                    
                    dominados.append(j)
                    dominacion = list(poblacion[i].dominacion)
                    poblacion[i] = poblacion[i]._replace(dominacion=[dominacion[0], dominados])  
                    dominacion = list(poblacion[j].dominacion)
                    contador_dominaciones = dominacion[0]+1                    
                    poblacion[j] = poblacion[j]._replace(dominacion=[contador_dominaciones, dominacion[1]])                                        
            j += 1
        i += 1

    # Se crea el primer rango
    rango_k = []
    cont_ind = 0    
    i = 0
    while i < len(poblacion):
        dominacion = list(poblacion[i].dominacion)
        if dominacion[0] == 0:
            rango_k.append(i)
            cont_ind += 1
        i += 1
    rangos = []
    rangos.append(rango_k)

    # Se crean los demas rangos
    crea_rango = True
    iter = 0
    while crea_rango and iter < 100:            
        rango_n = []                
        i = 0
        while i < len(poblacion):            
            for j in rango_k:   
                if poblacion[i] != poblacion[j]:     
                    dominacion_j = list(poblacion[j].dominacion)                
                    if dominacion_j[1] is not None and i in dominacion_j[1]:
                        dominacion_i = list(poblacion[i].dominacion)
                        contador_dominaciones = dominacion_i[0]-1                    
                        poblacion[i] = poblacion[i]._replace(dominacion=[contador_dominaciones, dominacion_i[1]])
                        if contador_dominaciones == 0:
                            rango_n.append(i)
                            cont_ind += 1
                j += 1
            i += 1
        rangos.append(rango_n)
        if cont_ind == len(poblacion):
            break
        rango_k = rango_n 
        iter += 1   
    rangos = limpiar_lista(rangos)    

    return rangos

# Ordena la poblacion de acuerdo al ordenamiento por distancia de aglomeracion, crowding distance sorting
def ordenamiento_por_distancia_de_aglomeracion(poblacion, rangos, capacidad):
    # Por cada individuo de los rangos se obtiene la distancia de aglomeracion y se ordena cada rango de acuerdo a esa distancia
    indice_pob = 0
    for rango in rangos:
        rango_de_poblacion = []
        indice = indice_pob
        # Se recupera los individuos de un rango
        for ind in rango:
            rango_de_poblacion.append(poblacion[indice])
            indice += 1

        # Se ordena el rango de acuerdo a la evaluacion de cada individuo
        rango_de_poblacion = sorted(rango_de_poblacion, key=lambda individuo: evaluar_individuo(individuo, capacidad).evaluacion)    

        # Se calcula la distancia de aglomeracion de cada individuo del rango
        rango_de_poblacion[0] = rango_de_poblacion[0]._replace(distancia=math.inf)        
        rango_de_poblacion[len(rango_de_poblacion)-1] = rango_de_poblacion[len(rango_de_poblacion)-1]._replace(distancia=math.inf)        
        ind = 0
        while ind < len(rango_de_poblacion):
            if rango_de_poblacion[ind] is not rango_de_poblacion[0] and rango_de_poblacion[ind] is not rango_de_poblacion[len(rango_de_poblacion)-1]:
                distancia_ind = poblacion[ind].distancia
                if rango_de_poblacion[len(rango_de_poblacion)-1].evaluacion - rango_de_poblacion[0].evaluacion != 0:
                    rango_de_poblacion[ind] = rango_de_poblacion[ind]._replace(distancia=distancia_ind+(rango_de_poblacion[ind+1].evaluacion - rango_de_poblacion[ind-1].evaluacion)/(rango_de_poblacion[len(rango_de_poblacion)-1].evaluacion - rango_de_poblacion[0].evaluacion))                                
            ind += 1

        # Se ordena el rango de acuerdo a la distancia de aglomeracion de cada individuo
        rango_de_poblacion = sorted(rango_de_poblacion, key=lambda individuo: individuo.distancia, reverse=True)

        # Se actualiza el nuevo orden de ese rango en la poblacion
        for individuo in rango_de_poblacion:
            poblacion[indice_pob] = individuo
            indice_pob += 1
    
    return poblacion

# Obtiene el mejor individuo de cierto rango
def obtiene_mejor_individuo_del_rango(rango):    
    mejor_individuo = Individuo(None, math.inf, 0, 0, 0, [0,None], 0)    
    iter = 0
    for individuo in rango:
        if iter == 0:
            mejor_individuo = individuo
        elif individuo.evaluacion < mejor_individuo.evaluacion:
            mejor_individuo = individuo
        iter += 1
    return mejor_individuo

# Obtiene el peor individuo de cierto rango
def obtiene_peor_individuo_del_rango(rango):    
    peor_individuo = Individuo(None, 0, 0, 0, 0, [0,None], 0)    
    iter = 0
    for individuo in rango:
        if iter == 0:
            peor_individuo = individuo
        elif individuo.evaluacion > peor_individuo.evaluacion:
            peor_individuo = individuo
        iter += 1
    return peor_individuo

# Aplica el algoritmo NSGA-II de acuerdo a los datos que se reciben
def alg_NSGA2(num_nodos, num_camiones, coordenadas, horario, capacidad):    
    mejor_solucion = Individuo(None, 0, 0, 0, 0, [0,None], 0)
    peor_solucion = Individuo(None, 0, 0, 0, 0, [0,None], 0)            

    # Inicializa poblacion
    poblacion = genera_poblacion(int(num_nodos), int(num_camiones), coordenadas, horario)    

    gen = 0
    while gen < 100:
        mejor_solucion_actual = Individuo(None, 0, 0, 0, 0, [0,None], 0)
        peor_solucion_actual = Individuo(None, 0, 0, 0, 0, [0,None], 0)
        print(f'Generación = {gen+1}')
        # Se agregan individuos a la poblacion
        iter = 0
        while iter < 50:
            # Evaluacion de la poblacion
            evaluar_poblacion(poblacion, int(capacidad))            
            # Seleccion por torneo de padres    
            padre1, padre2 = seleccion_por_torneo(poblacion, int(capacidad))
            # Cruza de permutaciones
            hijo1, hijo2 = cruza_de_permutaciones(poblacion[padre1].solucion, poblacion[padre2].solucion, random.uniform(0.6, 0.9))
            # Mutacion de los hijos
            hijo1 = mutacion(hijo1.solucion, random.uniform(0.01, 0.1))
            hijo2 = mutacion(hijo2.solucion, random.uniform(0.01, 0.1))
            # Se agregan los hijos a la poblacion
            poblacion.append(hijo1)
            poblacion.append(hijo2)
            iter += 1  
        tamanio_poblacion = len(poblacion)

        # Evaluacion de la poblacion
        evaluar_poblacion(poblacion, int(capacidad))        
        # Aplica ordenamiento no determinado a la poblacion
        orden_indices = ordenamiento_no_determinado(poblacion)                  
        copia_poblacion = poblacion
        ind = 0
        # Ordena la poblacion de acuerdo a la lista de indices que se obtuvo
        for rango in orden_indices:
            for indice in rango:
                poblacion[ind] = copia_poblacion[indice]
                ind += 1        
        # Aplica ordenamiento por distancia de aglomeracion a la poblacion
        poblacion = ordenamiento_por_distancia_de_aglomeracion(poblacion, orden_indices, capacidad)    
        # Se eliminan los ultimos elementos de la poblacion
        copia_poblacion = poblacion.copy()
        ind = 0
        while ind < tamanio_poblacion:
            if ind >= tamanio_poblacion/2:
                poblacion.remove(copia_poblacion[ind])            
            ind += 1
        
        mejores_de_rangos = []
        peores_de_rangos = []
        inicio = 0
        # Se obtiene el mejor y el peor de cada rango
        for rango in orden_indices:
            mejor = obtiene_mejor_individuo_del_rango(poblacion[inicio:inicio+len(rango)-1])            
            mejores_de_rangos.append(mejor)
            peor = obtiene_peor_individuo_del_rango(poblacion[inicio:inicio+len(rango)-1])            
            peores_de_rangos.append(peor)
            inicio = len(rango)-1          

        # Se busca el mejor de la generacion
        for individuo in mejores_de_rangos:
            if gen == 1:
                mejor_solucion = individuo               
            if mejor_solucion_actual.evaluacion == 0:
                mejor_solucion_actual = individuo                 
            if individuo.evaluacion < mejor_solucion_actual.evaluacion:
                mejor_solucion_actual = individuo
        y_mejor_actual.append(mejor_solucion_actual.evaluacion)

        # Se actualiza la mejor solucion encontrada
        if mejor_solucion_actual.evaluacion < mejor_solucion.evaluacion:
            mejor_solucion = mejor_solucion_actual
        y_mejor.append(mejor_solucion.evaluacion)

        # Se busca el peor de la generacion
        for individuo in peores_de_rangos:
            if gen == 1:
                peor_solucion = individuo               
            if peor_solucion_actual.evaluacion == 0:
                peor_solucion_actual = individuo        
            if individuo.evaluacion > peor_solucion_actual.evaluacion:
                peor_solucion_actual = individuo
        y_peor_actual.append(peor_solucion_actual.evaluacion)

        # Se actualiza la peor solucion encontrada
        if peor_solucion_actual.evaluacion > peor_solucion.evaluacion:
            peor_solucion = peor_solucion_actual
        y_peor.append(peor_solucion.evaluacion)

        # Se obtiene el promedio de la evaluacion de los individuos de la poblacion
        promedio(poblacion)
        gen += 1

    # Recupera las evaluaciones de cada individuo de la poblacion final
    for individuo in poblacion:
        trayectos_soluciones.append(individuo.evaluacion_trayecto)
        cargas_soluciones.append(individuo.evaluacion_carga)
        tiempos_soluciones.append(individuo.evaluacion_tiempo)

    # Se agrega las evaluaciones de la mejor solucion que se haya encontrado durante todo el proceso
    if mejor_solucion != mejor_solucion_actual:
        trayectos_soluciones.append(mejor_solucion.evaluacion_trayecto)
        cargas_soluciones.append(mejor_solucion.evaluacion_carga)
        tiempos_soluciones.append(mejor_solucion.evaluacion_tiempo)

    return mejor_solucion

# Función para generar un nombre de archivo único
def obtener_nombre(base_name, extension, nombre_archivo):
    ruta = './output'      
    os.makedirs(ruta,exist_ok=True)  
    carpeta_rem = f'{nombre_archivo}-Graficas' 
    ruta_carpeta = os.path.join(ruta, carpeta_rem)
    counter = 1
    filename = f"{base_name}{extension}"
    while os.path.exists(f'{ruta_carpeta}/{filename}'):
        filename = f"{base_name}_{counter}{extension}"
        counter += 1
    return filename

if __name__ == '__main__':
    ruta_archivo = sys.argv[1]
    nombre_archivo = os.path.basename(ruta_archivo)
    numN, numC, capacidad, coordenadas = leer_archivo(ruta_archivo)
    print(f"\nCantidad de nodos: {numN}")
    print(f"Cantidad de camiones: {numC}")
    print(f"Capacidad de cada camión: {capacidad}")
    print(f"Coordenadas: \n{coordenadas}\n")

    horario_establecido = False
    while not horario_establecido:
        try:
            hora_inicio = input("Ingresa la hora de inicio, en formato de 24 hrs y que tenga la siguiente forma: HH:MM:SS\n")
            hora_fin = input("Ingresa la hora final, en formato de 24 hrs y que tenga la siguiente forma: HH:MM:SS\n")

            if time.fromisoformat(hora_inicio) > time.fromisoformat(hora_fin) or time.fromisoformat(hora_inicio) == time.fromisoformat(hora_fin):
                print("ERROR: Ingresa un horario correcto.")
            else:
                horario_establecido = True
        except ValueError:
            print("ERROR: Ingresa el horario con el formato que se indica.")

    horario = [hora_inicio, hora_fin]
    comienzo = perf_counter()
    solucion = alg_NSGA2(numN, numC, coordenadas, horario, int(capacidad))    
    fin = perf_counter()
    print(f"Mejor solución = {solucion.solucion}")
    print(f"Evaluación = {solucion.evaluacion}")
    print(f"Evaluación de trayecto = {solucion.evaluacion_trayecto}")
    print(f"Evaluación de carga = {solucion.evaluacion_carga}")
    print(f"Evaluación de tiempo = {solucion.evaluacion_tiempo}")
    print(f"\nTiempo en que finalizo el algoritmo NSGA2 = {fin-comienzo} seg")
    
    # DataFrame para almacenar los resultados
    resultados = pd.DataFrame(columns=['Ejecución', 'Cantidad_Contenedores', 'Cantidad_Camiones', 'Capacidad_Camion', 'Horario', 'Mejor_Solucion', 'Evaluacion_Final', 'Evaluacion_Trayecto', 'Evaluacion_Carga', 'Evaluacion_Tiempo'])

    # Agregar resultados al DataFrame
    resultados = resultados._append({'Ejecución': 1, 'Cantidad_Contenedores': numN, 'Cantidad_Camiones': numC, 'Capacidad_Camion': capacidad, 'Horario': horario, 'Mejor_Solucion': solucion.solucion, 'Evaluacion_Final': solucion.evaluacion, 'Evaluacion_Trayecto': solucion.evaluacion_trayecto, 'Evaluacion_Carga': solucion.evaluacion_carga, 'Evaluacion_Tiempo': solucion.evaluacion_tiempo}, ignore_index=True)

    # Guardar los resultados en un archivo CSV
    nombre_archivo = f'{nombre_archivo}_resultados_NSGA2.csv'
    num_lineas = 0
    try:
        # Si el archivo existe
        df = pd.read_csv(nombre_archivo)        

        # Abrir el archivo CSV y contar las líneas
        with open(nombre_archivo, 'r') as archivo_csv:
            lector_csv = csv.reader(archivo_csv)
            for fila in lector_csv:
                num_lineas += 1

        df = pd.concat([df, resultados], ignore_index=True)
        ultima_fila = df.shape[0]-1
        df.loc[ultima_fila,'Ejecución'] = num_lineas
        df.to_csv(nombre_archivo, index=False)
    except FileNotFoundError:
        # Si el archivo no existe, crear uno nuevo vacío
        resultados.to_csv(nombre_archivo, index=False)
        num_lineas += 1

    # Creamos la ruta para guardar las graficas
    ruta = './output'      
    os.makedirs(ruta,exist_ok=True)  
    carpeta = f'{nombre_archivo}-Graficas' 
    ruta_carpeta = os.path.join(ruta, carpeta)
    if os.path.exists(ruta_carpeta) and os.path.isdir(ruta_carpeta):
        os.makedirs(ruta_carpeta,exist_ok=True) 
    else:
        os.makedirs(ruta_carpeta)         
    carpeta_ejec = f'{num_lineas}-Ejecucion' 
    ruta_ejecucion = os.path.join(ruta_carpeta, carpeta_ejec)
    os.makedirs(ruta_ejecucion)

    # Crea grafica con la mejor, peor y el promedio de las aptitudes de cada generacion
    x_generacion = np.linspace(0, 100, 100)
    plt.plot(x_generacion, y_mejor, label='Mejor')
    plt.plot(x_generacion, y_peor, label='Peor')
    plt.plot(x_generacion, y_promedio, label='Promedio')
    plt.title('NSGA-II con la optimización de rutas')
    plt.xlabel('Generación')
    plt.ylabel('Aptitud')
    plt.legend(loc='upper right')
    plt.xlim(1,100)
    base = f"{nombre_archivo}-mejor_peor_y_promedio"
    extension = ".png"
    nombre = obtener_nombre(base, extension, nombre_archivo)
    ruta_imagen = os.path.join(ruta_ejecucion, nombre)
    plt.savefig(ruta_imagen)
    plt.show()    

    # Crea grafica con la mejor actual, peor actual y el promedio de las aptitudes de cada generacion
    x_generacion = np.linspace(0, 100, 100)
    plt.plot(x_generacion, y_mejor_actual, label='Mejor actual')
    plt.plot(x_generacion, y_peor_actual, label='Peor actual')
    plt.plot(x_generacion, y_promedio, label='Promedio')
    plt.title('NSGA-II con la optimización de rutas')
    plt.xlabel('Generación')
    plt.ylabel('Aptitud')
    plt.legend(loc='upper right')
    plt.xlim(1,100)
    base = f"{nombre_archivo}-mejor_act_peor_act_y_promedio"
    extension = ".png"
    nombre = obtener_nombre(base, extension, nombre_archivo)
    ruta_imagen = os.path.join(ruta_ejecucion, nombre)
    plt.savefig(ruta_imagen)    
    plt.show()
     
    # Crea grafica de las soluciones finales de la poblacion con respecto a la evaluacion de su tiempo y carga de residuos    
    fig, ax = plt.subplots()    
    for x, y in zip(tiempos_soluciones, cargas_soluciones):         
        if x == solucion.evaluacion_tiempo and y == solucion.evaluacion_carga:
            ax.scatter(x, y, color='red', marker='o', zorder=5)
        else:
            ax.scatter(x, y, color='blue', marker='o')
    plt.title('Evaluación del tiempo y carga de las soluciones')
    plt.xlabel('Tiempo')
    plt.ylabel('Carga')
    base = f"{nombre_archivo}-tiempo_y_carga"
    extension = ".png"
    nombre = obtener_nombre(base, extension, nombre_archivo)
    ruta_imagen = os.path.join(ruta_ejecucion, nombre)
    plt.savefig(ruta_imagen)
    plt.show()    

    # Crea grafica de las soluciones finales de la poblacion con respecto a la evaluacion de su tiempo y trayecto    
    fig, ax = plt.subplots()    
    for x, y in zip(tiempos_soluciones, trayectos_soluciones):         
        if x == solucion.evaluacion_tiempo and y == solucion.evaluacion_trayecto:
            ax.scatter(x, y, color='red', marker='o', zorder=5)
        else:
            ax.scatter(x, y, color='blue', marker='o')
    plt.title('Evaluación del tiempo y distancia de las soluciones')
    plt.xlabel('Tiempo')
    plt.ylabel('Distancia')
    base = f"{nombre_archivo}-tiempo_y_distancia"
    extension = ".png"
    nombre = obtener_nombre(base, extension, nombre_archivo)
    ruta_imagen = os.path.join(ruta_ejecucion, nombre)
    plt.savefig(ruta_imagen)
    plt.show()    

    # Crea grafica de las soluciones finales de la poblacion con respecto a la evaluacion de carga de residuos y trayecto    
    fig, ax = plt.subplots()    
    for x, y in zip(cargas_soluciones, trayectos_soluciones):         
        if x == solucion.evaluacion_carga and y == solucion.evaluacion_trayecto:
            ax.scatter(x, y, color='red', marker='o', zorder=5)
        else:
            ax.scatter(x, y, color='blue', marker='o')      
    plt.title('Evaluación de la carga y distancia de las soluciones')
    plt.xlabel('Carga')
    plt.ylabel('Distancia')
    base = f"{nombre_archivo}-carga_y_distancia"
    extension = ".png"
    nombre = obtener_nombre(base, extension, nombre_archivo)
    ruta_imagen = os.path.join(ruta_ejecucion, nombre)
    plt.savefig(ruta_imagen)
    plt.show()    

    # Crea grafica 3d de las soluciones finales de la poblacion con respecto a todas sus evaluaciones
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for x, y, z in zip(tiempos_soluciones, trayectos_soluciones, cargas_soluciones):         
        if x == solucion.evaluacion_tiempo and y == solucion.evaluacion_trayecto and z == solucion.evaluacion_carga:
            ax.scatter(x, y, z, color='red', marker='o', zorder=5)
        else:
            ax.scatter(x, y, z, color='blue', marker='o')   
    ax.set_xlabel('Tiempo')
    ax.set_ylabel('Distancia')
    ax.set_zlabel('Carga de residuos')
    plt.title('Evaluación de todos los objetivos de las soluciones')
    base = f"{nombre_archivo}-tiempo_distancia_y_carga"
    extension = ".png"
    nombre = obtener_nombre(base, extension, nombre_archivo)
    ruta_imagen = os.path.join(ruta_ejecucion, nombre)
    plt.savefig(ruta_imagen)
    plt.show()