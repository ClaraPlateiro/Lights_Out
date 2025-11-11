import random
import tkinter as tk
from tkinter import ttk, messagebox
from resuelve_lights_out import resuelve_lights_out  # tu función

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
        self.title("Lights Out — Demo mínima (𝔽₂)")
        self.geometry("980x680")
        self.minsize(820, 580)
        self.configure(bg=BG)

        self.n = tk.IntVar(value=5)
        self.tablero = [[0]*5 for _ in range(5)]
        self._ultima_sol = None
        self._animando = False
        self._markers = [] 

        style = ttk.Style()
        try: style.theme_use("clam")
        except: pass
        style.configure(".", background=BG, foreground=TEXT)
        style.configure("TLabel", background=BG, foreground=TEXT)
        style.configure("TButton", padding=8)
        style.map("TButton", background=[("active", "#23304a")])

        top = ttk.Frame(self); top.pack(side=tk.TOP, fill=tk.X, padx=14, pady=10)
        ttk.Label(top, text="Tamaño n:").pack(side=tk.LEFT)
        self.nspin = tk.Spinbox(
            top, from_=MIN_N, to=MAX_N, textvariable=self.n, width=5,
            command=self._cambiar_n, bg="#141B2A", fg=TEXT,
            insertbackground=TEXT, readonlybackground="#141B2A",
            relief="flat", highlightthickness=0, bd=1
        )
        self.nspin.pack(side=tk.LEFT, padx=6)

        self.btn_nuevo = ttk.Button(top, text="Nuevo", command=self._nuevo); self.btn_nuevo.pack(side=tk.LEFT, padx=6)
        self.btn_rand  = ttk.Button(top, text="Aleatorio", command=self._aleatorio); self.btn_rand.pack(side=tk.LEFT, padx=6)
        self.btn_calc  = ttk.Button(top, text="Calcular solución", command=self._calcular); self.btn_calc.pack(side=tk.LEFT, padx=10)
        self.btn_apply = ttk.Button(top, text="Aplicar solución", command=self._aplicar); self.btn_apply.pack(side=tk.LEFT, padx=6)

        main = ttk.Frame(self); main.pack(fill=tk.BOTH, expand=True, padx=14, pady=8)
        self.canvas = tk.Canvas(main, bg=BOARD, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda _e: self._redibujar())
        self.canvas.bind("<Button-1>", self._click)

        self._redibujar()

    def _metricas(self):
        n = self.n.get()
        W = max(self.canvas.winfo_width(), 640)
        H = max(self.canvas.winfo_height(), 480)
        usable_w = W - 2*MARGIN
        usable_h = H - 2*MARGIN
        cell = int(min(usable_w, usable_h)/n) - 4
        cell = max(CELL_MIN, min(cell, CELL_MAX))
        grid_w = n*cell; grid_h = n*cell
        ox = (W - grid_w)//2; oy = (H - grid_h)//2
        return n, cell, ox, oy

    def _redibujar(self):
        self.canvas.delete("all")
        self._markers.clear()
        n, cell, ox, oy = self._metricas()
        self.rects = [[None]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                x1, y1 = ox + j*cell, oy + i*cell
                x2, y2 = x1 + cell, y1 + cell
                r = max(6, int(cell*0.18))
               
                self.canvas.create_rectangle(x1+r, y1, x2-r, y2, fill=TILE, outline=BORD, width=1)
                self.canvas.create_rectangle(x1, y1+r, x2, y2-r, fill=TILE, outline=BORD, width=1)
                self.canvas.create_oval(x1, y1, x1+2*r, y1+2*r, fill=TILE, outline=BORD, width=1)
                self.canvas.create_oval(x2-2*r, y1, x2, y1+2*r, fill=TILE, outline=BORD, width=1)
                self.canvas.create_oval(x2-2*r, y2-2*r, x2, y2, fill=TILE, outline=BORD, width=1)
                self.canvas.create_oval(x1, y2-2*r, x1+2*r, y2, fill=TILE, outline=BORD, width=1)
               
                pad = max(5, int(cell*0.12))
                fill = ON if self.tablero[i][j] else OFF
                rect = self.canvas.create_rectangle(x1+pad, y1+pad, x2-pad, y2-pad, fill=fill, outline="")
                self.rects[i][j] = rect

        if self._ultima_sol:
            self._marcar_solucion(self._ultima_sol)

    def _refrescar_colores(self):
        n, _, _, _ = self._metricas()
        for i in range(n):
            for j in range(n):
                self.canvas.itemconfig(self.rects[i][j], fill=(ON if self.tablero[i][j] else OFF))

    def _marcar_solucion(self, x_vec):
        self._clear_markers()
        n, cell, ox, oy = self._metricas()
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

            halo = self.canvas.create_rectangle(x1, y1, x2, y2, fill=ACCENT, outline="", stipple="gray25")
            self._markers.append(halo)

            
            outer = self.canvas.create_rectangle(x1, y1, x2, y2, outline=ACCENT, width=3)
            inner = self.canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2, outline=ACCENT_LIGHT, width=1)
            self._markers.extend([outer, inner])

            
            self._markers.append(self.canvas.create_line(x1, y1, x1+corner, y1, fill=ACCENT_LIGHT, width=3, capstyle="round"))
            self._markers.append(self.canvas.create_line(x1, y1, x1, y1+corner, fill=ACCENT_LIGHT, width=3, capstyle="round"))
            
            self._markers.append(self.canvas.create_line(x2, y1, x2-corner, y1, fill=ACCENT_LIGHT, width=3, capstyle="round"))
            self._markers.append(self.canvas.create_line(x2, y1, x2, y1+corner, fill=ACCENT_LIGHT, width=3, capstyle="round"))
         
            self._markers.append(self.canvas.create_line(x1, y2, x1+corner, y2, fill=ACCENT_LIGHT, width=3, capstyle="round"))
            self._markers.append(self.canvas.create_line(x1, y2, x1, y2-corner, fill=ACCENT_LIGHT, width=3, capstyle="round"))
            
            self._markers.append(self.canvas.create_line(x2, y2, x2-corner, y2, fill=ACCENT_LIGHT, width=3, capstyle="round"))
            self._markers.append(self.canvas.create_line(x2, y2, x2, y2-corner, fill=ACCENT_LIGHT, width=3, capstyle="round"))

    def _clear_markers(self):
        for mid in self._markers:
            self.canvas.delete(mid)
        self._markers = []

    def _click(self, e):
        if self._animando:
            return
        n, cell, ox, oy = self._metricas()
        i = (e.y - oy)//cell
        j = (e.x - ox)//cell
        if 0 <= i < n and 0 <= j < n:
            self.tablero[i][j] ^= 1
            self._refrescar_colores()
            self._ultima_sol = None
            self._clear_markers()

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
        self.tablero = [[0]*nn for _ in range(nn)]
        self._redibujar()
        self._ultima_sol = None

    def _nuevo(self):
        if self._animando:
            return
        n = self.n.get()
        self.tablero = [[0]*n for _ in range(n)]
        self._redibujar()
        self._ultima_sol = None

    def _aleatorio(self):
        if self._animando:
            return
        n = self.n.get()
        self.tablero = [[1 if random.random() < 0.5 else 0 for _ in range(n)] for _ in range(n)]
        self._redibujar()
        self._ultima_sol = None

    def _calcular(self):
        if self._animando:
            return
        try:
            x = resuelve_lights_out(self.tablero)
        except Exception:
            messagebox.showwarning("Sin solución", "b ∉ Col(A). Este tablero no tiene solución.")
            self._ultima_sol = None
            self._clear_markers()
            return

        self._ultima_sol = x
        self._marcar_solucion(x)

    def _aplicar(self):
        if self._animando:
            return
        x = self._ultima_sol
        if x is None:
            self._calcular()
            x = self._ultima_sol
            if x is None:
                return

        coords = []
        n = self.n.get()
        for k, bit in enumerate(x):
            if bit == 1:
                coords.append(divmod(k, n))

        if not coords:
            messagebox.showinfo("Listo", "No hay celdas que presionar (ya está resuelto).")
            return

        self._animando = True
        self._toggle_botones(False)
        self._clear_markers()
        self._animar_aplicacion(coords, paso=0)

    def _animar_aplicacion(self, coords, paso):
        if paso >= len(coords):
            self._animando = False
            self._toggle_botones(True)
            self._refrescar_colores()
            if all(v == 0 for fila in self.tablero for v in fila):
                messagebox.showinfo("Listo", "✔ Solución aplicada. Tablero en 0.")
            else:
                messagebox.showwarning("Aviso", "Se aplicó la solución, pero no quedó todo en 0.")
            self._ultima_sol = None
            return

        i, j = coords[paso]
        self._resaltar_celda(i, j)
        self.after(POST_HL_MS, lambda: self._aplicar_pulso_y_continuar(coords, paso, i, j))

    def _aplicar_pulso_y_continuar(self, coords, paso, i, j):
        self._aplicar_pulso(i, j)
        self._refrescar_colores()
        self.after(STEP_GAP_MS, lambda: self._animar_aplicacion(coords, paso+1))

    def _resaltar_celda(self, i, j):
        n, cell, ox, oy = self._metricas()
        pad = max(5, int(cell*0.12))
        x1 = ox + j*cell + pad
        y1 = oy + i*cell + pad
        x2 = ox + (j+1)*cell - pad
        y2 = oy + (i+1)*cell - pad
        hl = self.canvas.create_rectangle(x1, y1, x2, y2, fill=ACCENT, outline="")
        self.after(HIGHLIGHT_MS, lambda: self.canvas.delete(hl))

    def _aplicar_pulso(self, i, j):
        n = self.n.get()
        for di, dj in ((0,0), (1,0), (-1,0), (0,1), (0,-1)):
            r, c = i + di, j + dj
            if 0 <= r < n and 0 <= c < n:
                self.tablero[r][c] ^= 1

    def _toggle_botones(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        for b in (self.btn_nuevo, self.btn_rand, self.btn_calc, self.btn_apply):
            b.configure(state=state)
        self.nspin.configure(state=("normal" if enabled else "disabled"))

def main():
    App().mainloop()

if __name__ == "__main__":
    main()
