import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SistemaDifuso:
    def __init__(self):
        self.lista_habilidades = ["Lógica", "Creatividad", "Trabajo en equipo", "Análisis", "Empatía"]
        self.lista_intereses = ["Tecnología", "Arte", "Investigación", "Relaciones humanas", "Negocios"]

        # Definición de variables difusas
        self.habilidades = {hab: ctrl.Antecedent(np.arange(0, 6, 1), hab) for hab in self.lista_habilidades}
        self.intereses = {interes: ctrl.Antecedent(np.arange(0, 6, 1), interes) for interes in self.lista_intereses}

        self.categorias_carreras = {
            "Ingeniería": ctrl.Consequent(np.arange(0, 1.1, 0.1), 'ingenieria'),
            "Administración": ctrl.Consequent(np.arange(0, 1.1, 0.1), 'administracion'),
            "Ciencias de la Salud": ctrl.Consequent(np.arange(0, 1.1, 0.1), 'salud'),
            "Humanidades": ctrl.Consequent(np.arange(0, 1.1, 0.1), 'humanidades'),
            "Artes": ctrl.Consequent(np.arange(0, 1.1, 0.1), 'artes'),
        }

        # Definir las funciones de membresía
        self.definir_funciones_membresia()
        # Definir las reglas del sistema
        self.definir_reglas()
        # Crear el sistema de control
        self.crear_sistema_control()

    def definir_funciones_membresia(self):
        """Define funciones de membresía trapezoidales para habilidades e intereses"""
        for variable in list(self.habilidades.values()) + list(self.intereses.values()):
            variable['bajo'] = fuzz.trapmf(variable.universe, [0, 0, 1, 2])
            variable['medio'] = fuzz.trapmf(variable.universe, [1, 2, 3, 4])
            variable['alto'] = fuzz.trapmf(variable.universe, [3, 4, 5, 5])
        for categoria in self.categorias_carreras.values():
            # Funciones trapezoidales para las categorías
            categoria['bajo'] = fuzz.trapmf(categoria.universe, [0, 0, 0.1, 0.3])
            categoria['medio'] = fuzz.trapmf(categoria.universe, [0.2, 0.4, 0.6, 0.8])
            categoria['alto'] = fuzz.trapmf(categoria.universe, [0.7, 0.9, 1, 1])

    def definir_reglas(self):
        """Define reglas mejoradas para activar correctamente los valores medio y alto"""
        self.reglas = []
        categorias = {
            "Ingeniería": ("Lógica", "Tecnología"),
            "Artes": ("Creatividad", "Arte"),
            "Administración": ("Análisis", "Negocios"),
            "Humanidades": ("Trabajo en equipo", "Relaciones humanas"),
            "Ciencias de la Salud": ("Empatía", "Investigación"),
        }

        for categoria, (habilidad, interes) in categorias.items():
            # Bajo (más flexible)
            self.reglas.append(ctrl.Rule(self.habilidades[habilidad]['bajo'] | self.intereses[interes]['bajo'], 
                                         self.categorias_carreras[categoria]['bajo']))

            # Medio (permitiendo combinaciones con valores altos)
            self.reglas.append(ctrl.Rule((self.habilidades[habilidad]['medio'] & self.intereses[interes]['medio']) |
                                         (self.habilidades[habilidad]['alto'] & self.intereses[interes]['medio']) |
                                         (self.habilidades[habilidad]['medio'] & self.intereses[interes]['alto']),
                                         self.categorias_carreras[categoria]['medio']))

            # Alto (requiere que al menos uno sea alto y otro medio)
            self.reglas.append(ctrl.Rule(self.habilidades[habilidad]['alto'] & self.intereses[interes]['alto'], 
                                         self.categorias_carreras[categoria]['alto']))

        print(f"✅ Se han definido {len(self.reglas)} reglas para el sistema difuso.")

    def crear_sistema_control(self):
        """Crea el sistema de control difuso"""
        print(f"Cantidad de reglas definidas: {len(self.reglas)}")
        if not self.reglas:
            raise ValueError("Error: No se han definido reglas difusas.")
        self.controlador = ctrl.ControlSystem(self.reglas)
        self.simulador = ctrl.ControlSystemSimulation(self.controlador)

    def calcular_carreras(self, habilidades_valores, intereses_valores):
        """Ejecuta el sistema difuso con los valores proporcionados"""
        for hab, valor in habilidades_valores.items():
            self.simulador.input[hab] = valor
        for interes, valor in intereses_valores.items():
            self.simulador.input[interes] = valor

        try:
            self.simulador.compute()
        except Exception as e:
            print(f"Error en la simulación: {e}")
            return {"error": "No se pudo ejecutar el sistema difuso."}

        resultados = {cat: self.simulador.output[var.label] for cat, var in self.categorias_carreras.items()}
        return resultados

    def graficar_membresia(self):
        """Muestra las funciones de membresía en una ventana con scroll y organizadas en tres columnas."""
        root = tk.Toplevel()
        root.title("Funciones de Membresía")

        # Establecer un tamaño específico para la ventana (ajusta según tus necesidades)
        root.geometry("800x600")  # Puedes cambiar las dimensiones a lo que prefieras
        
        # Frame principal con scrollbar
        frame = tk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(frame)
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scroll_frame = tk.Frame(canvas)  # Frame para las gráficas

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        habilidades = self.habilidades
        intereses = self.intereses
        categorias = self.categorias_carreras
        num_filas = max(len(habilidades), len(intereses), len(categorias))

        fig, axes = plt.subplots(nrows=num_filas, ncols=3, figsize=(12, 3 * num_filas))
        axes = np.reshape(axes, (num_filas, 3))

        # Graficar funciones de membresía para las habilidades
        for i, (nombre, var) in enumerate(habilidades.items()):
            for etiqueta in ['bajo', 'medio', 'alto']:
                if etiqueta in var.terms:
                    axes[i, 0].plot(var.universe, var[etiqueta].mf, label=etiqueta)
            axes[i, 0].set_title(f"Habilidad: {nombre}")
            axes[i, 0].legend()

        # Graficar funciones de membresía para los intereses
        for i, (nombre, var) in enumerate(intereses.items()):
            for etiqueta in ['bajo', 'medio', 'alto']:
                if etiqueta in var.terms:
                    axes[i, 1].plot(var.universe, var[etiqueta].mf, label=etiqueta)
            axes[i, 1].set_title(f"Interés: {nombre}")
            axes[i, 1].legend()

        # Graficar funciones de membresía para las categorías
        for i, (nombre, var) in enumerate(categorias.items()):
            for etiqueta in ['bajo', 'medio', 'alto']:
                if etiqueta in var.terms:
                    axes[i, 2].plot(var.universe, var[etiqueta].mf, label=etiqueta)
            axes[i, 2].set_title(f"Categoría: {nombre}")
            axes[i, 2].legend()

        plt.subplots_adjust(hspace=0.5, wspace=0.3)
        canvas_fig = FigureCanvasTkAgg(fig, master=scroll_frame)
        canvas_fig.draw()
        canvas_fig.get_tk_widget().pack()

        # Botón para continuar y cerrar
        def cerrar_ventana():
            root.destroy()

        ttk.Button(root, text="Continuar", command=cerrar_ventana).pack()

        root.mainloop()
