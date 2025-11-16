# Lights Out (𝔽₂)

Implementación en Python del problema "Lights Out" sobre el cuerpo 𝔽₂.

- Un solver algebraico (`resuelve_lights_out.py`) que resuelve el sistema Ax = b por eliminación de Gauss en 𝔽₂.
- Una interfaz gráfica (`front_lights_out.py`) que muestra **dos tableros**: izquierdo para jugar manualmente y derecho para calcular/animar la solución.
- Un script de experimentos (`experimentos_stats.py`) para estudiar rango, nulidad y proporción de tableros resolubles.

---

**Requisitos**

- Python 3.7+ (recomendado)
- `tkinter` (normalmente incluido en instalaciones estándar de Python en Windows/macOS)

No hay dependencias externas adicionales.

---

**Archivos principales**

- `resuelve_lights_out.py` — función `resuelve_lights_out(tablero: List[List[int]]) -> List[int]`.  
  También puede ejecutarse desde consola y leer un tablero desde stdin.

- `front_lights_out.py` — interfaz Tkinter con dos tableros:

  - izquierdo: tablero de juego (clics del usuario),
  - derecho: tablero modelo donde se calcula y aplica la solución.

- `experimentos_stats.py` — script para correr ensayos masivos y obtener estadísticas (rango, nulidad y proporción muestral de tableros con solución).

---

## Uso (PowerShell)

### 1. Ejecutar la interfaz gráfica (dos tableros)

Desde la carpeta del proyecto (la misma que contiene los archivos `.py`), ejecutar:

```powershell
py front_lights_out.py
# o
python front_lights_out.py
```

Flujo básico:

- Cambiar **Tamaño n** para seleccionar un tablero n×n.
- Definir el tablero inicial:
  - manualmente haciendo clic en las casillas (modo configuración), o
  - usando el botón **Aleatorio**.
- Si querés limpiar todo, usar **Nuevo**.

Uso principal:

- Pulsar **Jugar**: el tablero izquierdo pasa a ser el tablero de juego manual (cada clic aplica la cruz real del juego). El tablero derecho queda congelado con la misma configuración inicial, reservado para el modelo.
- Pulsar **Calcular solución**: el tablero derecho marcará las celdas que el modelo debe presionar según el sistema Ax = b.
- Pulsar **Aplicar solución**: se anima, paso a paso, cómo el modelo presiona esas casillas y cómo el tablero derecho se apaga.

Este programa sirve tanto para mostrar la dinámica del juego (tablero izquierdo) como para visualizar la solución algebraica sobre el mismo tablero inicial (tablero derecho).

---

### 2. Ejecutar el solver por consola

```powershell
py resuelve_lights_out.py
# o
python resuelve_lights_out.py
```

Formato de entrada (ejemplo interactivo):

```
3
0 1 0
1 1 0
0 0 1
```

El script imprime:

- el vector solución `x`,
- la matriz de presiones,
- las coordenadas a presionar,
- el tablero final para verificar que quedó todo en 0.

También podés pasar la entrada por un here-string en PowerShell:

```powershell
@"
3
0 1 0
1 1 0
0 0 1
"@ | py resuelve_lights_out.py
```

---

### 3. Ejecutar experimentos masivos

```powershell
py experimentos_stats.py
# o
python experimentos_stats.py
```

El script:

- recorre tamaños `n = 2 … 10`;
- para cada `n`:
  - construye la matriz `A` según la regla de la cruz,
  - calcula rango y nulidad en 𝔽₂,
  - genera `M = 10000` tableros aleatorios (semilla fija `SEED = 12345`),
  - intenta resolver cada uno con `resuelve_lights_out`.

Imprime una tabla con columnas:

```
n | rango | nulidad | resueltos | no resueltos | proporción muestral
```

Estos resultados son los que se comentan en la sección de Resultados y Discusión del informe.
