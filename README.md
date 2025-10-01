# Optimizador de Rutas con Algoritmo Genético Multiobjetivo (NSGA-II)

Este proyecto implementa el algoritmo evolutivo NSGA-II para resolver un problema de optimización de rutas de camiones recolectores de residuos.
El programa recibe un archivo de entrada con los nodos, coordenadas y demandas, y genera rutas eficientes considerando múltiples objetivos: distancia recorrida, carga transportada y tiempo empleado.

Durante la ejecución se muestran estadísticas y se generan gráficas comparativas del desempeño de las soluciones.

## 📋 Requisitos

- Python 3.8 o superior
- Pip (gestor de paquetes de Python)

## 📦 Instalación

1. Clona este repositorio.

2. Instala las dependencias necesarias.

```bash
pip install numpy matplotlib pandas
```
O puedes instarlas directamente con:
```bash
pip install -r requirements.txt
```

3. Ejecuta el programa desde la terminal:

```bash
python3 src/alg_nsga2.py output/ejemplares/[Nombre del archivo de un ejemplar].txt
```
Por ejemplo:
```bash
python3 src/alg_nsga2.py output/ejemplares/A-n32-k5.txt
```

## 🧪 Uso de un entorno virtual (recomendado)

Para mantener las dependencias del proyecto organizadas, puedes usar un entorno virtual de Python.

### 🔧 Crear y activar el entorno virtual

1. Crea el entorno virtual (una sola vez):

```bash
python -m venv venv
```

2. Activa el entorno virtual:

- En **Windows**:
  ```cmd
  venv\Scripts\activate
  ```

- En **Linux/macOS**:
  ```bash
  source venv/bin/activate
  ```

3. Instala las dependencias necesarias dentro del entorno:

```bash
pip install numpy matplotlib pandas
```
O puedes instarlas directamente con:
```bash
pip install -r requirements.txt
```

4. Ejecuta el programa:

```bash
python3 .\src\alg_nsga2.py .\output\ejemplares\[Nombre del archivo de un ejemplar].txt
```
Por ejemplo:
```bash
python3 .\src\alg_nsga2.py .\output\ejemplares\A-n32-k5.txt
```

5. Cuando termines, puedes desactivar el entorno virtual con:

```bash
deactivate
```

## 🚀 Uso

1. Prepara un archivo de entrada .txt con el siguiente formato (ejemplo estilo TSPLIB):
```python-repl
NAME : k3
DIMENSION : 10
CAPACITY : 50
NODE_COORD_SECTION
1 23 45
2 12 67
...
DEMAND_SECTION
1 0
2 10
...
DEPOT_SECTION
0
```

2. Ejecuta el programa y proporciona por consola la hora de inicio y fin de la jornada de los camiones:
```ruby
Ingresa la hora de inicio, en formato HH:MM:SS
Ingresa la hora final, en formato HH:MM:SS
```

3. El algoritmo evolutivo NSGA-II se ejecutará durante 100 generaciones y mostrará los resultados:
- Mejor solución encontrada
- Evaluación final
- Evaluaciones por trayecto, carga y tiempo
- Tiempo total de ejecución

4. Se generan automáticamente gráficas en la carpeta output/ con:
- Evolución de las aptitudes (mejor, peor y promedio).
- Comparativas entre tiempo, carga y distancia.
- Visualización 3D de las soluciones.

Los resultados también se almacenan en un archivo CSV con las ejecuciones acumuladas.

## 🧠 Funcionalidades clave

- **Lectura de datos** desde archivo .txt (coordenadas, demanda, capacidad de camiones).
- **Generación de población inicial** con rutas aleatorias.
- **Algoritmo evolutivo NSGA-II** (selección por torneo, cruza, mutación).
- **Múltiples objetivos**: tiempo, carga y trayecto.
- **Gráficas automáticas** de la evolución y soluciones finales.
- **Resultados persistentes** en archivos CSV y carpetas de ejecución.

## 📝 Ejemplo de ejecución

```bash
python3 .\src\alg_nsga2.py .\output\ejemplares\A-n32-k5.txt
```

```bash
Cantidad de nodos: 32
Cantidad de camiones: 5
Capacidad de cada camión: 100
Coordenadas: [...]
Ingresa la hora de inicio, en formato de 24 hrs y que tenga la siguiente forma: HH:MM:SS
08:00:00
Ingresa la hora final, en formato de 24 hrs y que tenga la siguiente forma: HH:MM:SS
22:00:00
Generación = 1
Generación = 2
...
Mejor solución = [...]
Evaluación = 1393711
Evaluación de trayecto = 2193
Evaluación de carga = 248410
Evaluación de tiempo = 1005
```

## 📊 Análisis de resultados
Además del script principal alg_nsga2.py, este proyecto incluye alg_nsga2_por_ejemplar.py, el cual permite analizar de forma estadística las ejecuciones guardadas en los archivos CSV generados por el algoritmo NSGA-II.

### 🔧 Ejecución
Corre el script desde la terminal:
```bash
python3 alg_nsga2_por_ejemplar.py
```
El programa mostrará un menú para seleccionar el ejemplar (archivo de resultados CSV) que quieras analizar:
```bash
Selecciona un ejemplar:
 1. A-n32-k5
 2. A-n63-k10
 3. E-n101-k14
 4. M-n200-k17
 5. X-n153-k22
 6. Salir del programa
```

### 📈 Resultados obtenidos
El script procesará las evaluaciones de las soluciones y mostrará:
- Mejor valor → La solución más óptima encontrada.
- Peor valor → El desempeño más bajo registrado.
- Media → Promedio de todas las ejecuciones.
- Mediana → Valor central de los resultados ordenados.
- Desviación estándar → Medida de dispersión de los resultados.

## Contenido del repositorio
- src / <--- carpeta con el código fuente de la implementación
- output / <--- carpeta con gráficas, que evaluan la carga y la distancia de las soluciones, y con ejemplares para probar el algoritmo
- ejecuciones.csv <-- hoja de cálculo con la información de las ejecuciones realizadas

## 🛠 Autor y créditos
Este proyecto fue desarrollado como parte de un trabajo de Cómputo Evolutivo, aplicando NSGA-II para optimizar problemas de logística y rutas.
