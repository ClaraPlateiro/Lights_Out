import random
from typing import List
from resuelve_lights_out import resuelve_lights_out  # tu solver

M = 10000
SEED = 12345

def vecinos_cruz(i, j, n):
    for di, dj in ((0,0),(1,0),(-1,0),(0,1),(0,-1)):
        r, c = i+di, j+dj
        if 0 <= r < n and 0 <= c < n:
            yield r, c

def a_idx(i, j, n): 
    return i*n + j

def construir_A_bitfilas(n: int) -> List[int]:
    """Devuelve A como lista de filas en bitset (int) de tamaño n^2."""
    tam = n*n
    A = [0]*tam
    for i in range(n):
        for j in range(n):
            fila = a_idx(i, j, n)
            bits = 0
            for r in range(n):
                for c in range(n):
                    if (i, j) in vecinos_cruz(r, c, n):
                        bits |= (1 << a_idx(r, c, n))
            A[fila] = bits
    return A

def rango_F2(filas_bits: List[int]) -> int:
    """Rango por Gauss binario con filas como bitsets."""
    A = filas_bits[:]
    rank = 0
    m = max((x.bit_length() for x in A), default=0)
    for col in range(m-1, -1, -1):
        piv = -1
        for r in range(rank, len(A)):
            if (A[r] >> col) & 1:
                piv = r
                break
        if piv == -1:
            continue
        if piv != rank:
            A[rank], A[piv] = A[piv], A[rank]
        for r in range(len(A)):
            if r != rank and ((A[r] >> col) & 1):
                A[r] ^= A[rank]
        rank += 1
        if rank == len(A):
            break
    return rank

def nulidad_y_rango(n: int):
    A = construir_A_bitfilas(n)
    rank = rango_F2(A)
    nullity = n*n - rank
    return rank, nullity

def tablero_random(n: int):
    return [[random.randint(0,1) for _ in range(n)] for _ in range(n)]

def aplicar(tab, plan):
    """Aplica plan (vector 0/1) al tablero y devuelve el final."""
    n = len(tab)
    out = [fila[:] for fila in tab]
    for k, bit in enumerate(plan):
        if bit:
            i, j = divmod(k, n)
            for di, dj in ((0,0),(1,0),(-1,0),(0,1),(0,-1)):
                r, c = i+di, j+dj
                if 0 <= r < n and 0 <= c < n:
                    out[r][c] ^= 1
    return out

if __name__ == "__main__":
    random.seed(SEED)
    col_prop = "Proporción muestral (resueltos/M)"
    print(f"Muestras uniformes por tamaño: M={M} (semilla={SEED})\n")
    print(f" n | rango | nulidad | resueltos | no resueltos | {col_prop}")
    print(  "---+-------+---------+-----------+--------------+------------------------------")

    for n in range(2, 11):
        rango, nulidad = nulidad_y_rango(n)

        resueltos = 0
        no_resueltos = 0
        for _ in range(M):
            b = tablero_random(n)
            try:
                x = resuelve_lights_out(b)
                fin = aplicar(b, x)
                if all(v == 0 for fila in fin for v in fila):
                    resueltos += 1
                else:
                    no_resueltos += 1  # poco probable si el solver es correcto
            except ValueError:
                no_resueltos += 1     # b ∉ Col(A)

        prop = resueltos / M
        print(f"{n:>2d} | {rango:>5d} | {nulidad:>7d} | {resueltos:>9d} | {no_resueltos:>12d} | {prop:>28.6f}")
