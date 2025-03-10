import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

class SistemaDifuso:
    def __init__(self):
        self.lista_habilidades = ["Lógica", "Creatividad", "Trabajo en equipo", "Análisis", "Empatía"]
        self.lista_intereses = ["Tecnología", "Arte", "Investigación", "Relaciones humanas", "Negocios"]

        self.habilidades = {hab: ctrl.Antecedent(np.arange(0, 6, 1), hab) for hab in self.lista_habilidades}
        self.intereses = {interes: ctrl.Antecedent(np.arange(0, 6, 1), interes) for interes in self.lista_intereses}

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
        """Define funciones de membresía con mejor ajuste"""
        for variable in list(self.habilidades.values()) + list(self.intereses.values()):
            variable['bajo'] = fuzz.trimf(variable.universe, [0, 0, 2.5])
            variable['medio'] = fuzz.trimf(variable.universe, [2, 3, 4])
            variable['alto'] = fuzz.trimf(variable.universe, [3.5, 5, 5])

        for categoria in self.categorias_carreras.values():
            categoria['bajo'] = fuzz.trimf(categoria.universe, [0, 0, 0.3])
            categoria['medio'] = fuzz.trimf(categoria.universe, [0.2, 0.5, 0.8])
            categoria['alto'] = fuzz.trimf(categoria.universe, [0.6, 1, 1])

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
        """Calcula el grado de pertenencia de las carreras según las habilidades e intereses"""
        for hab, valor in habilidades_valores.items():
            self.simulador.input[hab] = valor
        for interes, valor in intereses_valores.items():
            self.simulador.input[interes] = valor

        try:
            self.simulador.compute()
        except Exception as e:
            print(f"Error en la simulación: {e}")
            return {"error": "No se pudo ejecutar el sistema difuso."}

        resultados = {cat: self.simulador.output.get(var.label, 0) for cat, var in self.categorias_carreras.items()}
        return resultados

    def graficar_todas_membresias(self):
        """Genera todas las gráficas de membresía sin errores de índice"""
        todas_variables = {**self.habilidades, **self.intereses, **self.categorias_carreras}
        num_vars = len(todas_variables)
        num_filas = (num_vars // 4) + (1 if num_vars % 4 else 0)

        fig, axes = plt.subplots(num_filas, 4, figsize=(15, 10))
        axes = axes.ravel()[:num_vars]  # Ajusta la cantidad de gráficos al número de variables

        for i, (nombre, var) in enumerate(todas_variables.items()):
            for etiqueta in ['bajo', 'medio', 'alto']:
                if etiqueta in var.terms:
                    axes[i].plot(var.universe, var[etiqueta].mf, label=etiqueta)
            axes[i].set_title(nombre)
            axes[i].legend()

        plt.tight_layout()
        plt.show()

    def graficar_resultados(self, resultados):
        """Genera un gráfico con los grados de pertenencia de las carreras"""
        fig, ax = plt.subplots(figsize=(7, 5))

        categorias, valores = zip(*resultados.items())
        ax.bar(categorias, valores, color=['blue', 'green', 'red', 'orange', 'purple'])
        ax.set_xlabel("Carreras")
        ax.set_ylabel("Grado de Pertenencia")
        ax.set_title("Grados de Pertenencia a las Carreras (0 a 1)")
        ax.set_ylim(0, 1)

        plt.xticks(rotation=15)
        plt.show()

