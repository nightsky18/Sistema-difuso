import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

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
            variable['bajo'] = fuzz.trimf(variable.universe, [0, 0, 2])
            variable['medio'] = fuzz.trimf(variable.universe, [1, 2.5, 4])
            variable['alto'] = fuzz.trimf(variable.universe, [3, 5, 5])

        for categoria in self.categorias_carreras.values():
            categoria['bajo'] = fuzz.trimf(categoria.universe, [0, 0, 0.5])
            categoria['medio'] = fuzz.trimf(categoria.universe, [0.3, 0.5, 0.7])
            categoria['alto'] = fuzz.trimf(categoria.universe, [0.6, 1, 1])

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
        """Genera gráficos de membresía para cada habilidad e interés."""
        for nombre, var in {**self.habilidades, **self.intereses}.items():
            plt.figure(figsize=(6, 4))
            for etiqueta in ['bajo', 'medio', 'alto']:
                plt.plot(var.universe, fuzz.trimf(var.universe, [0, 0, 2]) if etiqueta == 'bajo' else
                         fuzz.trimf(var.universe, [1, 2.5, 4]) if etiqueta == 'medio' else
                         fuzz.trimf(var.universe, [3, 5, 5]), label=etiqueta)
            plt.title(f"Función de Membresía - {nombre}")
            plt.xlabel("Grado")
            plt.ylabel("Membresía")
            plt.legend()
            plt.show()

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
