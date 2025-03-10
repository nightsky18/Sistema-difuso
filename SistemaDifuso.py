import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

class SistemaDifuso:
    def __init__(self):
        self.lista_habilidades = ["Lógica", "Creatividad", "Trabajo en equipo", "Análisis", "Empatía"]
        self.lista_intereses = ["Tecnología", "Arte", "Investigación", "Relaciones humanas", "Negocios"]

        self.habilidades = {hab: ctrl.Antecedent(np.arange(0, 6, 1), hab) for hab in self.lista_habilidades}
        self.intereses = {int: ctrl.Antecedent(np.arange(0, 6, 1), int) for int in self.lista_intereses}

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
        for variable in list(self.habilidades.values()) + list(self.intereses.values()):
            variable['bajo'] = fuzz.trimf(variable.universe, [0, 0, 2])
            variable['medio'] = fuzz.trimf(variable.universe, [1, 2.5, 4])
            variable['alto'] = fuzz.trimf(variable.universe, [3, 5, 5])

        for categoria in self.categorias_carreras.values():
            categoria['bajo'] = fuzz.trimf(categoria.universe, [0, 0, 0.5])
            categoria['medio'] = fuzz.trimf(categoria.universe, [0.3, 0.5, 0.7])
            categoria['alto'] = fuzz.trimf(categoria.universe, [0.6, 1, 1])

    def definir_reglas(self):
        self.reglas = []

        for hab in self.habilidades.values():
            self.reglas.append(ctrl.Rule(hab['alto'], self.categorias_carreras["Ingeniería"]['alto']))
            self.reglas.append(ctrl.Rule(hab['bajo'], self.categorias_carreras["Ingeniería"]['bajo']))

        for int in self.intereses.values():
            self.reglas.append(ctrl.Rule(int['alto'], self.categorias_carreras["Artes"]['alto']))
            self.reglas.append(ctrl.Rule(int['bajo'], self.categorias_carreras["Artes"]['bajo']))

        # Reglas para administración
        self.reglas.append(ctrl.Rule(self.habilidades["Lógica"]['alto'], self.categorias_carreras["Administración"]['alto']))
        self.reglas.append(ctrl.Rule(self.habilidades["Lógica"]['bajo'], self.categorias_carreras["Administración"]['bajo']))
        self.reglas.append(ctrl.Rule(self.intereses["Negocios"]['alto'], self.categorias_carreras["Administración"]['alto']))
        self.reglas.append(ctrl.Rule(self.intereses["Negocios"]['bajo'], self.categorias_carreras["Administración"]['bajo']))

    def crear_sistema_control(self):
        print(f"Cantidad de reglas definidas: {len(self.reglas)}")
        if not self.reglas:
            raise ValueError("Error: No se han definido reglas difusas.")

        self.controlador = ctrl.ControlSystem(self.reglas)
        self.simulador = ctrl.ControlSystemSimulation(self.controlador)

    def calcular_carreras(self, habilidades_valores, intereses_valores):
        for hab, valor in habilidades_valores.items():
            self.simulador.input[hab] = valor
        for int, valor in intereses_valores.items():
            self.simulador.input[int] = valor

        try:
            self.simulador.compute()
        except Exception as e:
            print(f"Error en la simulación: {e}")
            return {"error": "No se pudo ejecutar el sistema difuso."}

        resultados = {}
        for cat, var in self.categorias_carreras.items():
            key = var.label
            resultados[cat] = self.simulador.output.get(key, 0)  # Evita KeyError asignando 0 si no hay salida

        return resultados

    def graficar_todas_membresias(self):
        """Genera todas las gráficas de membresía en una sola ventana."""
        fig, axes = plt.subplots(3, 4, figsize=(15, 10))
        axes = axes.ravel()

        todas_variables = {**self.habilidades, **self.intereses, **self.categorias_carreras}

        for i, (nombre, var) in enumerate(todas_variables.items()):
            for etiqueta in ['bajo', 'medio', 'alto']:
                if etiqueta in var.terms:
                    axes[i].plot(var.universe, fuzz.trimf(var.universe, [0, 0, 2]) if etiqueta == 'bajo' else
                                 fuzz.trimf(var.universe, [1, 2.5, 4]) if etiqueta == 'medio' else
                                 fuzz.trimf(var.universe, [3, 5, 5]), label=etiqueta)
            axes[i].set_title(nombre)
            axes[i].legend()

        plt.tight_layout()
        plt.show()

    def graficar_resultados(self, resultados):
        """Genera un gráfico con los grados de pertenencia de las carreras."""
        fig, ax = plt.subplots(figsize=(7, 5))

        categorias, valores = zip(*resultados.items())
        ax.bar(categorias, valores, color=['blue', 'green', 'red', 'orange', 'purple'])
        ax.set_xlabel("Carreras")
        ax.set_ylabel("Grado de Pertenencia")
        ax.set_title("Grados de Pertenencia a las Carreras (0 a 1)")
        ax.set_ylim(0, 1)

        plt.xticks(rotation=15)
        plt.show()
