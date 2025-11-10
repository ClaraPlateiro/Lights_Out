# resuelve_lights_out.py
# Función que resuelve Lights Out con Gauss en 𝔽₂ usando SOLO sumas de filas (Fi <- Fi + Fj).
from typing import List

def resuelve_lights_out(tablero: List[List[int]]) -> List[int]:
    """
    Resuelve Lights Out sobre 𝔽₂ mediante eliminación gaussiana usando únicamente sumas de filas (XOR).
    Parámetro:
      tablero: matriz n×n con 0/1 que representa el estado inicial (1 = luz encendida)
    Devuelve:
      x: vector de largo n^2 con 0/1; x[k]=1 indica presionar la celda k (orden por filas, 0-based)
    Lanza:
      ValueError si el sistema es inconsistente (no tiene solución).
    """

    # ---------- utilidades de índice y vecindad ----------
    def a_indice(i: int, j: int, n: int) -> int:
        return i * n + j

    def vecinos_cruz(i: int, j: int, n: int):
        for di, dj in ((0,0), (1,0), (-1,0), (0,1), (0,-1)):
            r, c = i + di, j + dj
            if 0 <= r < n and 0 <= c < n:
                yield r, c

    # ---------- construcción de A (filas como bitsets) y b ----------
    def construir_A_bitfilas(n: int):
        tam = n * n
        A_bits = [0] * tam
        for i in range(n):
            for j in range(n):
                fila = a_indice(i, j, n)
                bitfila = 0
                # Columna (r,c) afecta a (i,j) si (i,j) está en la "cruz" de (r,c)
                for r in range(n):
                    for c in range(n):
                        if (i, j) in vecinos_cruz(r, c, n):
                            col = a_indice(r, c, n)
                            bitfila |= (1 << col)
                A_bits[fila] = bitfila
        return A_bits

    def construir_b_bits(tab: List[List[int]]) -> int:
        n = len(tab)
        b = 0
        for i in range(n):
            for j in range(n):
                if tab[i][j] & 1:
                    b |= (1 << (i*n + j))
        return b

    def bits_a_vector(x_bits: int, n: int) -> List[int]:
        tam = n * n
        return [(x_bits >> k) & 1 for k in range(tam)]

    # ---------- validaciones y armado ----------
    if not tablero or any(len(f) != len(tablero) for f in tablero):
        raise ValueError("El tablero debe ser una matriz n×n de 0/1.")

    n = len(tablero)
    A = construir_A_bitfilas(n)
    b_bits = construir_b_bits(tablero)
    tam = n * n

    b = [(b_bits >> i) & 1 for i in range(tam)]
    A = A[:]  # copia

    # ---------- Gauss en 𝔽₂ usando SOLO Fi <- Fi + Fj (XOR) ----------
    fila = 0
    for col in range(tam):
        if fila >= tam:
            break
        # Activar pivote en (fila, col) sumando alguna fila inferior con 1 en esa columna
        if ((A[fila] >> col) & 1) == 0:
            origen = -1
            for r in range(fila + 1, tam):
                if ((A[r] >> col) & 1) == 1:
                    origen = r
                    break
            if origen != -1:
                A[fila] ^= A[origen]
                b[fila] ^= b[origen]
        # Si sigue 0, no hay pivote en esta columna
        if ((A[fila] >> col) & 1) == 0:
            continue
        # Eliminar debajo del pivote
        for r in range(fila + 1, tam):
            if ((A[r] >> col) & 1) == 1:
                A[r] ^= A[fila]
                b[r] ^= b[fila]
        fila += 1

    # Inconsistencia: fila de A nula con término independiente 1
    for r in range(tam):
        if A[r] == 0 and b[r] == 1:
            raise ValueError("Sin solución: b no pertenece al espacio columna de A (b ∉ Col(A)).")

    # Leer pivotes y limpiar por arriba (también con sumas)
    columnas_pivote = []
    puntero = 0
    for col in range(tam):
        if puntero < tam and ((A[puntero] >> col) & 1) == 1:
            columnas_pivote.append((puntero, col))
            puntero += 1
    for idx in range(len(columnas_pivote) - 1, -1, -1):
        r, c = columnas_pivote[idx]
        for rr in range(0, r):
            if ((A[rr] >> c) & 1) == 1:
                A[rr] ^= A[r]
                b[rr] ^= b[r]

    # Variables libres = 0 -> solución particular
    x_bits = 0
    for r, c in columnas_pivote:
        if b[r] & 1:
            x_bits |= (1 << c)

    return bits_a_vector(x_bits, n)


def _print_matriz_int(matriz: List[List[int]], titulo: str = "", ancho: int = 1):
    if titulo:
        print(f"\n{titulo}")
    n = len(matriz)
    for i in range(n):
        print("  " + " ".join(f"{matriz[i][j]:>{ancho}d}" for j in range(n)))

def _print_matriz_indices(n: int):
    print("\nMapa de índices (orden por filas):")
    k = 1
    filas = []
    for i in range(n):
        fila = []
        for j in range(n):
            fila.append(k)
            k += 1
        filas.append(fila)
    _print_matriz_int(filas, ancho=len(str(n*n)))

def _vector_a_matriz(v: List[int], n: int) -> List[List[int]]:
    return [v[i*n:(i+1)*n] for i in range(n)]

def _coords_desde_vector(x: List[int], n: int):
    return [(k // n + 1, k % n + 1) for k, bit in enumerate(x) if bit == 1]

def _aplicar_presion(tab: List[List[int]], i: int, j: int):
    n = len(tab)
    for di, dj in ((0,0), (1,0), (-1,0), (0,1), (0,-1)):
        r, c = i + di, j + dj
        if 0 <= r < n and 0 <= c < n:
            tab[r][c] ^= 1

def _simular_aplicacion(tablero: List[List[int]], x: List[int]) -> List[List[int]]:
    n = len(tablero)
    final = [fila[:] for fila in tablero]
    for k, bit in enumerate(x):
        if bit == 1:
            i, j = divmod(k, n)
            _aplicar_presion(final, i, j)
    return final


def _leer_tablero_desde_stdin():
    """
    Lee n y luego n filas de 0/1 separados por espacio desde stdin.
    Ejemplo:
      3
      0 1 0
      1 1 0
      0 0 1
    """
    n_line = input().strip()
    if n_line.lower().startswith("n"):
        # permitir "n = 3"
        n = int(n_line.split("=")[1])
    else:
        n = int(n_line)
    tablero = []
    for _ in range(n):
        fila = list(map(int, input().strip().split()))
        if len(fila) != n or any(v not in (0, 1) for v in fila):
            raise ValueError("Cada fila debe tener n valores 0/1.")
        tablero.append(fila)
    return tablero

if __name__ == "__main__":
    try:
        print("=== Lights Out en 𝔽₂ — Resolución por Gauss (solo sumas de filas) ===")
        print("Ingrese n y luego las n filas (0/1 separados por espacio).")
        print("Ejemplo:\n3\n0 1 0\n1 1 0\n0 0 1\n")
        tablero = _leer_tablero_desde_stdin()
        n = len(tablero)

        _print_matriz_int(tablero, titulo=f"Tablero inicial (n = {n})", ancho=1)
        _print_matriz_indices(n)
        print("\nNota: el vector x tiene longitud n² y está indexado por este mapa (1-based).")

        x = resuelve_lights_out(tablero)
        coords = _coords_desde_vector(x, n)
        presiones = _vector_a_matriz(x, n)
        movimientos = sum(x)

        print("\n\u2192 Vector solución x (0/1, orden por filas):")
        print("  " + " ".join(map(str, x)))
        _print_matriz_int(presiones, titulo="Matriz de presiones (1 = presionar esa casilla):", ancho=1)
        if coords:
            print("Coordenadas a presionar (fila,col):", " ".join(f"({i},{j})" for i, j in coords))
        else:
            print("No hay que presionar ninguna casilla (el tablero ya estaba resuelto).")
        print(f"Número de movimientos: {movimientos}")

        final = _simular_aplicacion(tablero, x)
        _print_matriz_int(final, titulo="Tablero final tras aplicar la solución:", ancho=1)
        if all(v == 0 for fila in final for v in fila):
            print("Verificación: ✔ El tablero final quedó todo en 0.")
        else:
            print("Verificación: ✖ El tablero final no quedó todo en 0 (revise la entrada).")

    except ValueError as e:
        print("\nSin solución o entrada inválida:", e)
