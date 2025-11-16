import random
import tkinter as tk
from tkinter import ttk, messagebox
from resuelve_lights_out import resuelve_lights_out  # importa tu función

ACCENT         = "#C087F5" 
ACCENT_LIGHT   = "#EAD9FF"
ON             = "#419DD3"
OFF            = "#3A4556" 
BG             = "#0B0F17" 
BOARD          = "#0E1526" 
TILE           = "#121C2F"
BORD           = "#0A101C"
TEXT           = "#E8EAF0"

HIGHLIGHT_MS = 400  
STEP_GAP_MS  = 440   
POST_HL_MS   = 380   

MIN_N, MAX_N = 2, 20
CELL_MIN, CELL_MAX = 28, 110
MARGIN = 40

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lights Out — Demo doble (𝔽₂)")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(bg=BG)

        # estado lógico
        self.n = tk.IntVar(value=5)
        n0 = self.n.get()
        self.tablero_inicial = [[0]*n0 for _ in range(n0)]  # configuración editable
        self.tablero_juego   = [fila[:] for fila in self.tablero_inicial]  # tablero donde se juega a mano
        self.tablero_modelo  = [fila[:] for fila in self.tablero_inicial]  # tablero para la solución
        self._ultima_sol = None
        self._animando = False
        self._markers_sol = []
        self.modo = "config"  # "config" o "juego"

        # estilos
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass
        style.configure(".", background=BG, foreground=TEXT)
        style.configure("TLabel", background=BG, foreground=TEXT)
        style.configure("TButton", padding=8)
        style.map("TButton", background=[("active", "#23304a")])

        # barra superior con TODOS los controles
        top = ttk.Frame(self)
        top.pack(side=tk.TOP, fill=tk.X, padx=14, pady=(10, 6))

        ttk.Label(top, text="Tamaño n:").pack(side=tk.LEFT)
        self.nspin = tk.Spinbox(
            top, from_=MIN_N, to=MAX_N, textvariable=self.n, width=5,
            command=self._cambiar_n, bg="#141B2A", fg=TEXT,
            insertbackground=TEXT, readonlybackground="#141B2A",
            relief="flat", highlightthickness=0, bd=1
        )
        self.nspin.pack(side=tk.LEFT, padx=6)

        self.btn_nuevo = ttk.Button(top, text="Nuevo tablero", command=self._nuevo)
        self.btn_nuevo.pack(side=tk.LEFT, padx=6)

        self.btn_rand  = ttk.Button(top, text="Aleatorio", command=self._aleatorio)
        self.btn_rand.pack(side=tk.LEFT, padx=6)

        self.btn_jugar = ttk.Button(top, text="Jugar", command=self._jugar)
        self.btn_jugar.pack(side=tk.LEFT, padx=10)

        self.btn_calc  = ttk.Button(top, text="Calcular solución", command=self._calcular_solucion)
        self.btn_calc.pack(side=tk.LEFT, padx=6)

        self.btn_apply = ttk.Button(top, text="Aplicar solución", command=self._aplicar_solucion)
        self.btn_apply.pack(side=tk.LEFT, padx=6)

        self.lbl_modo = ttk.Label(top, text="Modo: configuración inicial")
        self.lbl_modo.pack(side=tk.RIGHT, padx=6)

        # zona principal con dos tableros
        main = ttk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True, padx=14, pady=8)

        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

        right = ttk.Frame(main)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))

        ttk.Label(left, text="Tablero de juego (manual)").pack(side=tk.TOP, pady=(0, 4))
        self.canvas_juego = tk.Canvas(left, bg=BOARD, highlightthickness=0)
        self.canvas_juego.pack(fill=tk.BOTH, expand=True)
        self.canvas_juego.bind("<Configure>", lambda e: self._redibujar_todo())
        self.canvas_juego.bind("<Button-1>", lambda e: self._click(e, "juego"))

        ttk.Label(right, text="Tablero modelo / solución").pack(side=tk.TOP, pady=(0, 4))
        self.canvas_sol = tk.Canvas(right, bg=BOARD, highlightthickness=0)
        self.canvas_sol.pack(fill=tk.BOTH, expand=True)
        self.canvas_sol.bind("<Configure>", lambda e: self._redibujar_todo())
        self.canvas_sol.bind("<Button-1>", lambda e: self._click(e, "sol"))

        self.rects_juego = []
        self.rects_sol = []

        self._redibujar_todo()

    # -------- utilidades de estado --------
    def _set_modo(self, modo):
        self.modo = modo
        if modo == "config":
            self.lbl_modo.config(text="Modo: configuración inicial")
        else:
            self.lbl_modo.config(text="Modo: juego y solución")

    # -------- dibujo y métricas --------
    def _metricas(self, canvas):
        n = self.n.get()
        W = max(canvas.winfo_width(), 360)
        H = max(canvas.winfo_height(), 360)
        usable_w = W - 2*MARGIN
        usable_h = H - 2*MARGIN
        cell = int(min(usable_w, usable_h)/n) - 4
        cell = max(CELL_MIN, min(cell, CELL_MAX))
        grid_w = n * cell
        grid_h = n * cell
        ox = (W - grid_w)//2
        oy = (H - grid_h)//2
        return n, cell, ox, oy

    def _get_board_for_view(self, view):
        if self.modo == "config":
            return self.tablero_inicial
        else:
            return self.tablero_juego if view == "juego" else self.tablero_modelo

    def _redibujar_todo(self):
        self._redibujar_view("juego")
        self._redibujar_view("sol")

    def _redibujar_view(self, view):
        canvas = self.canvas_juego if view == "juego" else self.canvas_sol
        canvas.delete("all")
        board = self._get_board_for_view(view)
        n = self.n.get()
        n, cell, ox, oy = self._metricas(canvas)
        rects = [[None]*n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                x1 = ox + j*cell
                y1 = oy + i*cell
                x2 = x1 + cell
                y2 = y1 + cell
                r = max(6, int(cell*0.18))

                canvas.create_rectangle(x1+r, y1, x2-r, y2, fill=TILE, outline=BORD, width=1)
                canvas.create_rectangle(x1, y1+r, x2, y2-r, fill=TILE, outline=BORD, width=1)
                canvas.create_oval(x1, y1, x1+2*r, y1+2*r, fill=TILE, outline=BORD, width=1)
                canvas.create_oval(x2-2*r, y1, x2, y1+2*r, fill=TILE, outline=BORD, width=1)
                canvas.create_oval(x2-2*r, y2-2*r, x2, y2, fill=TILE, outline=BORD, width=1)
                canvas.create_oval(x1, y2-2*r, x1+2*r, y2, fill=TILE, outline=BORD, width=1)

                pad = max(5, int(cell*0.12))
                fill = ON if board[i][j] else OFF
                rect = canvas.create_rectangle(x1+pad, y1+pad, x2-pad, y2-pad, fill=fill, outline="")
                rects[i][j] = rect

        if view == "juego":
            self.rects_juego = rects
        else:
            self.rects_sol = rects
            if self._ultima_sol:
                self._marcar_solucion(self._ultima_sol)

    def _refrescar_colores_juego(self):
        board = self._get_board_for_view("juego")
        n, _, _, _ = self._metricas(self.canvas_juego)
        for i in range(n):
            for j in range(n):
                self.canvas_juego.itemconfig(
                    self.rects_juego[i][j],
                    fill=(ON if board[i][j] else OFF)
                )

    def _refrescar_colores_sol(self):
        board = self._get_board_for_view("sol")
        n, _, _, _ = self._metricas(self.canvas_sol)
        for i in range(n):
            for j in range(n):
                self.canvas_sol.itemconfig(
                    self.rects_sol[i][j],
                    fill=(ON if board[i][j] else OFF)
                )

    # -------- marcadores de solución (solo tablero derecho) --------
    def _clear_markers_sol(self):
        for mid in self._markers_sol:
            self.canvas_sol.delete(mid)
        self._markers_sol = []

    def _marcar_solucion(self, x_vec):
        self._clear_markers_sol()
        canvas = self.canvas_sol
        n, cell, ox, oy = self._metricas(canvas)
        pad = max(5, int(cell*0.12))
        corner = max(10, int(cell * 0.28))

        for k, bit in enumerate(x_vec):
            if bit != 1:
                continue
            i, j = divmod(k, n)
            x1 = ox + j*cell + pad
            y1 = oy + i*cell + pad
            x2 = ox + (j+1)*cell - pad
            y2 = oy + (i+1)*cell - pad

            halo = canvas.create_rectangle(x1, y1, x2, y2, fill=ACCENT, outline="", stipple="gray25")
            self._markers_sol.append(halo)

            outer = canvas.create_rectangle(x1, y1, x2, y2, outline=ACCENT, width=3)
            inner = canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2, outline=ACCENT_LIGHT, width=1)
            self._markers_sol.extend([outer, inner])

            self._markers_sol.append(canvas.create_line(x1, y1, x1+corner, y1, fill=ACCENT_LIGHT, width=3, capstyle="round"))
            self._markers_sol.append(canvas.create_line(x1, y1, x1, y1+corner, fill=ACCENT_LIGHT, width=3, capstyle="round"))

            self._markers_sol.append(canvas.create_line(x2, y1, x2-corner, y1, fill=ACCENT_LIGHT, width=3, capstyle="round"))
            self._markers_sol.append(canvas.create_line(x2, y1, x2, y1+corner, fill=ACCENT_LIGHT, width=3, capstyle="round"))

            self._markers_sol.append(canvas.create_line(x1, y2, x1+corner, y2, fill=ACCENT_LIGHT, width=3, capstyle="round"))
            self._markers_sol.append(canvas.create_line(x1, y2, x1, y2-corner, fill=ACCENT_LIGHT, width=3, capstyle="round"))

            self._markers_sol.append(canvas.create_line(x2, y2, x2-corner, y2, fill=ACCENT_LIGHT, width=3, capstyle="round"))
            self._markers_sol.append(canvas.create_line(x2, y2, x2, y2-corner, fill=ACCENT_LIGHT, width=3, capstyle="round"))

    # -------- interacción con clicks --------
    def _click(self, e, view):
        if self._animando:
            return

        canvas = self.canvas_juego if view == "juego" else self.canvas_sol
        n, cell, ox, oy = self._metricas(canvas)
        i = (e.y - oy)//cell
        j = (e.x - ox)//cell
        if not (0 <= i < n and 0 <= j < n):
            return

        if self.modo == "config":
            self.tablero_inicial[i][j] ^= 1
            self.tablero_juego  = [fila[:] for fila in self.tablero_inicial]
            self.tablero_modelo = [fila[:] for fila in self.tablero_inicial]
            self._ultima_sol = None
            self._clear_markers_sol()
            self._redibujar_todo()
        else:
            if view == "juego":
                self._aplicar_pulso_en_tablero(self.tablero_juego, i, j)
                self._refrescar_colores_juego()

    def _aplicar_pulso_en_tablero(self, board, i, j):
        n = self.n.get()
        for di, dj in ((0,0), (1,0), (-1,0), (0,1), (0,-1)):
            r, c = i + di, j + dj
            if 0 <= r < n and 0 <= c < n:
                board[r][c] ^= 1

    # -------- botones de configuración --------
    def _cambiar_n(self):
        if self._animando:
            return
        try:
            nn = int(self.n.get())
            if nn < MIN_N or nn > MAX_N:
                raise ValueError
        except Exception:
            messagebox.showerror("Valor inválido", f"n debe ser entero entre {MIN_N} y {MAX_N}.")
            return

        self.tablero_inicial = [[0]*nn for _ in range(nn)]
        self.tablero_juego   = [fila[:] for fila in self.tablero_inicial]
        self.tablero_modelo  = [fila[:] for fila in self.tablero_inicial]
        self._ultima_sol = None
        self._clear_markers_sol()
        self._set_modo("config")
        self._redibujar_todo()

    def _nuevo(self):
        if self._animando:
            return
        n = self.n.get()
        self.tablero_inicial = [[0]*n for _ in range(n)]
        self.tablero_juego   = [fila[:] for fila in self.tablero_inicial]
        self.tablero_modelo  = [fila[:] for fila in self.tablero_inicial]
        self._ultima_sol = None
        self._clear_markers_sol()
        self._set_modo("config")
        self._redibujar_todo()

    def _aleatorio(self):
        if self._animando:
            return
        n = self.n.get()
        self.tablero_inicial = [[1 if random.random() < 0.5 else 0 for _ in range(n)] for _ in range(n)]
        self.tablero_juego   = [fila[:] for fila in self.tablero_inicial]
        self.tablero_modelo  = [fila[:] for fila in self.tablero_inicial]
        self._ultima_sol = None
        self._clear_markers_sol()
        self._set_modo("config")
        self._redibujar_todo()

    def _jugar(self):
        if self._animando:
            return
        self.tablero_juego   = [fila[:] for fila in self.tablero_inicial]
        self.tablero_modelo  = [fila[:] for fila in self.tablero_inicial]
        self._ultima_sol = None
        self._clear_markers_sol()
        self._set_modo("juego")
        self._redibujar_todo()

    # -------- botones de solución (tablero derecho) --------
    def _calcular_solucion(self):
        if self._animando:
            return
        if self.modo != "juego":
            messagebox.showinfo("Información", "Primero fija el tablero inicial y pulsa 'Jugar'.")
            return
        try:
            x = resuelve_lights_out(self.tablero_modelo)
        except Exception:
            messagebox.showwarning("Sin solución", "b ∉ Col(A). Este tablero inicial no tiene solución.")
            self._ultima_sol = None
            self._clear_markers_sol()
            return
        self._ultima_sol = x
        self._marcar_solucion(x)

    def _aplicar_solucion(self):
        if self._animando:
            return
        if self.modo != "juego":
            messagebox.showinfo("Información", "Primero fija el tablero inicial y pulsa 'Jugar'.")
            return

        x = self._ultima_sol
        if x is None:
            self._calcular_solucion()
            x = self._ultima_sol
            if x is None:
                return

        n = self.n.get()
        coords = [divmod(k, n) for k, bit in enumerate(x) if bit == 1]
        if not coords:
            messagebox.showinfo("Listo", "No hay casillas que presionar (ya está resuelto).")
            return

        self._animando = True
        self._toggle_botones(False)
        self._clear_markers_sol()
        self._animar_aplicacion_sol(coords, paso=0)

    def _animar_aplicacion_sol(self, coords, paso):
        if paso >= len(coords):
            self._animando = False
            self._toggle_botones(True)
            self._refrescar_colores_sol()
            if all(v == 0 for fila in self.tablero_modelo for v in fila):
                messagebox.showinfo("Listo", "✔ Solución aplicada en el tablero modelo. Tablero en 0.")
            else:
                messagebox.showwarning("Aviso", "Se aplicó la solución, pero no quedó todo en 0.")
            self._ultima_sol = None
            return

        i, j = coords[paso]
        self._resaltar_celda_sol(i, j)
        self.after(POST_HL_MS, lambda: self._aplicar_pulso_y_continuar_sol(coords, paso, i, j))

    def _aplicar_pulso_y_continuar_sol(self, coords, paso, i, j):
        self._aplicar_pulso_en_tablero(self.tablero_modelo, i, j)
        self._refrescar_colores_sol()
        self.after(STEP_GAP_MS, lambda: self._animar_aplicacion_sol(coords, paso+1))

    def _resaltar_celda_sol(self, i, j):
        canvas = self.canvas_sol
        n, cell, ox, oy = self._metricas(canvas)
        pad = max(5, int(cell*0.12))
        x1 = ox + j*cell + pad
        y1 = oy + i*cell + pad
        x2 = ox + (j+1)*cell - pad
        y2 = oy + (i+1)*cell - pad
        hl = canvas.create_rectangle(x1, y1, x2, y2, fill=ACCENT, outline="")
        self.after(HIGHLIGHT_MS, lambda: canvas.delete(hl))

    def _toggle_botones(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        for b in (self.btn_nuevo, self.btn_rand, self.btn_jugar, self.btn_calc, self.btn_apply):
            b.configure(state=state)
        self.nspin.configure(state=("normal" if enabled else "disabled"))

def main():
    App().mainloop()

if __name__ == "__main__":
    main()
