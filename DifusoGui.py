import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from SistemaDifuso import SistemaDifuso

class DifusoGui:
    def __init__(self):
        self.sistema = SistemaDifuso()
        self.root = tk.Tk()
        self.root.title("Orientador Vocacional")
        self.root.geometry("600x700")

        # Crear marco principal
        frame = ttk.Frame(self.root, padding="10")
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Ingresa valores de 0 (bajo) a 5 (alto) para cada habilidad:", font=("Arial", 11)).pack(anchor="w")

        # Crear entradas para habilidades
        self.habilidad_entries = {}
        for hab in self.sistema.lista_habilidades:
            row = ttk.Frame(frame)
            row.pack(fill="x", padx=5, pady=2)
            ttk.Label(row, text=hab + ":", width=20).pack(side="left")
            entry = ttk.Entry(row, width=5)
            entry.pack(side="left")
            self.habilidad_entries[hab] = entry

        ttk.Label(frame, text="Ingresa valores de 0 (bajo) a 5 (alto) para cada interés:", font=("Arial", 11)).pack(anchor="w")

        # Crear entradas para intereses
        self.interes_entries = {}
        for int in self.sistema.lista_intereses:
            row = ttk.Frame(frame)
            row.pack(fill="x", padx=5, pady=2)
            ttk.Label(row, text=int + ":", width=20).pack(side="left")
            entry = ttk.Entry(row, width=5)
            entry.pack(side="left")
            self.interes_entries[int] = entry

        # Botón para ver funciones de membresía
        # self.boton_membresia = ttk.Button(frame, text="Ver Funciones de Membresía", command=self.mostrar_membresia)
        # self.boton_membresia.pack(pady=5)

        # Botón de Calcular
        self.boton_calcular = ttk.Button(frame, text="Calcular", command=self.obtener_resultados)
        self.boton_calcular.pack(pady=10)

        self.root.mainloop()
        
    def validar_entradas(self):  # <-- ¡Este método debe estar dentro de la clase!
        """Valida los valores ingresados y los convierte a flotantes."""
        try:
            habilidades_valores = {hab: float(entry.get()) for hab, entry in self.habilidad_entries.items()}
            intereses_valores = {int: float(entry.get()) for int, entry in self.interes_entries.items()}
        except ValueError:
            messagebox.showerror("Error", "Debes ingresar valores numéricos entre 0 y 5.")
            return None, None

        # Validar rango 0-5
        if any(v < 0 or v > 5 for v in habilidades_valores.values()) or any(v < 0 or v > 5 for v in intereses_valores.values()):
            messagebox.showerror("Error", "Los valores deben estar entre 0 y 5.")
            return None, None

        return habilidades_valores, intereses_valores

    def obtener_resultados(self):
        """Obtiene los valores de entrada y ejecuta el sistema difuso."""
        habilidades_valores, intereses_valores = self.validar_entradas()
        if habilidades_valores is None or intereses_valores is None:
            return

        # Ejecutar el sistema difuso
        resultados = self.sistema.calcular_carreras(habilidades_valores, intereses_valores)

        if "error" in resultados:
            messagebox.showerror("Error", resultados["error"])
            return

        # Mostrar gráficas de membresía con marcadores
        self.sistema.graficar_membresia(habilidades_valores, intereses_valores, resultados)
        self.mostrar_resultados(resultados)  # Mostrar mensaje y gráfica de barras

    def mostrar_resultados(self, resultados):
        """Muestra los resultados en una gráfica de barras."""
        categorias, valores = zip(*resultados.items())

        # Mensaje con los valores de pertenencia
        resultado_texto = "\n".join([f"{cat}: {valor:.2f}" for cat, valor in resultados.items()])
        messagebox.showinfo("Resultados", f"Grados de pertenencia a las carreras:\n\n{resultado_texto}")

        # Gráfico de barras con los resultados
        plt.figure(figsize=(7, 5))
        plt.bar(categorias, valores, color=['blue', 'green', 'red', 'orange', 'purple'])
        plt.xlabel("Carreras")
        plt.ylabel("Grado de Pertenencia")
        plt.title("Grados de Pertenencia a las Carreras (0 a 1)")
        plt.xticks(rotation=15)
        plt.ylim(0, 1)
        plt.show()

    def mostrar_membresia(self):
        """Genera gráficos de membresía para cada habilidad e interés."""
        self.sistema.graficar_membresia()
