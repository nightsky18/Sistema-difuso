import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SistemaDifuso:
    def __init__(self):
        # Definir las habilidades e intereses disponibles
        self.lista_habilidades = ["Lógica", "Creatividad", "Trabajo en equipo", "Análisis", "Empatía"]
        self.lista_intereses = ["Tecnología", "Arte", "Investigación", "Relaciones humanas", "Negocios"]

        # Definir las variables de entrada (0 a 5)
        self.habilidades = {hab: ctrl.Antecedent(np.arange(0, 6, 1), hab) for hab in self.lista_habilidades}
        self.intereses = {int: ctrl.Antecedent(np.arange(0, 6, 1), int) for int in self.lista_intereses}

        # Definir la variable de salida (carreras)
        self.categorias_carreras = {
            "Ingeniería": ctrl.Consequent(np.arange(0, 1.1, 0.1), 'ingenieria'),
            "Administración": ctrl.Consequent(np.arange(0, 1.1, 0.1), 'administracion'),
            "Ciencias de la Salud": ctrl.Consequent(np.arange(0, 1.1, 0.1), 'salud'),
            "Humanidades": ctrl.Consequent(np.arange(0, 1.1, 0.1), 'humanidades'),
            "Artes": ctrl.Consequent(np.arange(0, 1.1, 0.1), 'artes'),
        }

        self.definir_funciones_membresia()
        self.definir_reglas()
        self.crear_sistema_control()

    def definir_funciones_membresia(self):
        """Define funciones de membresía para habilidades e intereses"""
        for variable in list(self.habilidades.values()) + list(self.intereses.values()):
            variable['bajo'] = fuzz.trapmf(variable.universe, [0, 0, 1, 2])
            variable['medio'] = fuzz.trapmf(variable.universe, [1, 2, 3, 4])
            variable['alto'] = fuzz.trapmf(variable.universe, [3, 4, 5, 5])

        for categoria in self.categorias_carreras.values():
            categoria['bajo'] = fuzz.trapmf(categoria.universe, [0, 0, 0.2, 0.4])
            categoria['medio'] = fuzz.trapmf(categoria.universe, [0.2, 0.4, 0.6, 0.8])
            categoria['alto'] = fuzz.trapmf(categoria.universe, [0.6, 0.8, 1, 1])
            
    def definir_reglas(self):
        """Define reglas difusas reducidas para evitar sobrecarga."""
        self.reglas = []

        # Reglas basadas solo en nivel alto de habilidades e intereses
        for hab in self.habilidades.values():
            self.reglas.append(ctrl.Rule(hab['alto'], self.categorias_carreras["Ingeniería"]['alto']))
            self.reglas.append(ctrl.Rule(hab['bajo'], self.categorias_carreras["Ingeniería"]['bajo']))

        for int in self.intereses.values():
            self.reglas.append(ctrl.Rule(int['alto'], self.categorias_carreras["Artes"]['alto']))
            self.reglas.append(ctrl.Rule(int['bajo'], self.categorias_carreras["Artes"]['bajo']))

        # Reglas generales para todas las carreras
        self.reglas.append(ctrl.Rule(self.habilidades["Trabajo en equipo"]['alto'], self.categorias_carreras["Ciencias de la Salud"]['alto']))
        self.reglas.append(ctrl.Rule(self.intereses["Relaciones humanas"]['alto'], self.categorias_carreras["Humanidades"]['alto']))
        self.reglas.append(ctrl.Rule(self.habilidades["Lógica"]['alto'], self.categorias_carreras["Administración"]['alto']))

    def crear_sistema_control(self):
        """Crea el sistema difuso."""
        print(f"Cantidad de reglas definidas: {len(self.reglas)}")
        if not self.reglas:
            raise ValueError("Error: No se han definido reglas difusas.")
    
        self.controlador = ctrl.ControlSystem(self.reglas)
        self.simulador = ctrl.ControlSystemSimulation(self.controlador)

    def calcular_carreras(self, habilidades_valores, intereses_valores):
        """Ejecuta el sistema difuso con los valores proporcionados."""
        for hab, valor in habilidades_valores.items():
            self.simulador.input[hab] = valor
        for int, valor in intereses_valores.items():
            self.simulador.input[int] = valor

        try:
            self.simulador.compute()
        except Exception as e:
            print(f"Error en la simulación: {e}")
            return {"error": "No se pudo ejecutar el sistema difuso."}

        resultados = {cat: self.simulador.output[var.label] for cat, var in self.categorias_carreras.items()}
        return resultados

    def graficar_membresia(self):
        """Muestra las funciones de membresía en una ventana con scroll y organizadas en tres columnas."""

        # Crear la ventana de Tkinter
        root = tk.Toplevel()
        root.title("Funciones de Membresía")

        # Frame principal con scrollbar
        frame = tk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(frame)
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)

        scroll_frame = tk.Frame(canvas)  # Frame para las gráficas

        # Configurar el scroll
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Datos de habilidades, intereses y categorías
        habilidades = self.habilidades
        intereses = self.intereses
        categorias = self.categorias_carreras

        num_filas = max(len(habilidades), len(intereses), len(categorias))

        # Crear figura con 3 columnas (Habilidades, Intereses, Categorías)
        fig, axes = plt.subplots(nrows=num_filas, ncols=3, figsize=(12, 3 * num_filas))

        # Si solo hay una fila, convertir `axes` en una lista de listas
        if num_filas == 1:
            axes = np.array([axes])

        # Convertir `axes` en una matriz bidimensional para evitar errores de indexado
        axes = np.reshape(axes, (num_filas, 3))

        # Llenar la primera columna con habilidades
        for i, (nombre, var) in enumerate(habilidades.items()):
            for etiqueta in ['bajo', 'medio', 'alto']:  # Acceder a los términos definidos
                if etiqueta in var.terms:
                    axes[i, 0].plot(var.universe, var[etiqueta].mf, label=etiqueta)

            axes[i, 0].set_title(f"Habilidad: {nombre}", fontsize=10)
            axes[i, 0].set_xlabel("Grado")
            axes[i, 0].set_ylabel("Membresía")
            axes[i, 0].legend()

        # Llenar la segunda columna con intereses
        for i, (nombre, var) in enumerate(intereses.items()):
            for etiqueta in ['bajo', 'medio', 'alto']:  
                if etiqueta in var.terms:
                    axes[i, 1].plot(var.universe, var[etiqueta].mf, label=etiqueta)

            axes[i, 1].set_title(f"Interés: {nombre}", fontsize=10)
            axes[i, 1].set_xlabel("Grado")
            axes[i, 1].set_ylabel("Membresía")
            axes[i, 1].legend()

        # Llenar la tercera columna con categorías
        for i, (nombre_categoria, var) in enumerate(categorias.items()):
            for etiqueta in ['bajo', 'medio', 'alto']:  
                if etiqueta in var.terms:
                    axes[i, 2].plot(var.universe, var[etiqueta].mf, label=etiqueta)

            axes[i, 2].set_title(f"Categoría: {nombre_categoria}", fontsize=10)
            axes[i, 2].set_xlabel("Grado")
            axes[i, 2].set_ylabel("Membresía")
            axes[i, 2].legend()

        # Ajustar la distribución de los gráficos
        plt.subplots_adjust(hspace=0.5, wspace=0.3)

        # Insertar la figura en Tkinter
        canvas_fig = FigureCanvasTkAgg(fig, master=scroll_frame)
        canvas_fig.draw()
        canvas_fig.get_tk_widget().pack()

        root.mainloop()
    
    def graficar_resultados(self, resultados):
        """Genera gráfico con los grados de pertenencia de las carreras."""
        categorias, valores = zip(*resultados.items())

        plt.figure(figsize=(7, 5))
        plt.bar(categorias, valores, color=['blue', 'green', 'red', 'orange', 'purple'])
        plt.xlabel("Carreras")
        plt.ylabel("Grado de Pertenencia")
        plt.title("Grados de Pertenencia a las Carreras (0 a 1)")
        plt.xticks(rotation=15)
        plt.ylim(0, 1)
        plt.show()
