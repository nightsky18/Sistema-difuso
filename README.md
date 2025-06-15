#  Orientador Vocacional Difuso

Este proyecto implementa un sistema experto usando **lógica difusa** para orientar a los usuarios en su elección vocacional. A partir de las **habilidades** e **intereses** ingresados, el sistema recomienda carreras según el grado de pertenencia a cada categoría.

## Características

- Interfaz gráfica desarrollada en **Tkinter**.
- Sistema difuso creado con **scikit-fuzzy**.
- Visualización de resultados con **matplotlib**.
- Reglas definidas para 5 categorías de carreras:
  - Ingeniería
  - Administración
  - Ciencias de la Salud
  - Humanidades
  - Artes

## Requisitos

- Python 3.x
- scikit-fuzzy
- numpy
- matplotlib
- tkinter (normalmente viene con Python)

Puedes instalar los requerimientos con:

```bash
pip install numpy matplotlib scikit-fuzzy
```
## Estructura
- main.py: Inicia la aplicación.
- DifusoGui.py: Contiene la interfaz gráfica.
- SistemaDifuso.py: Lógica del sistema difuso (entradas, reglas y salida)

## Uso
- Ejecuta el archivo main.py.
- Ingresa valores entre 0 y 5 para tus habilidades e intereses.
- Haz clic en "Calcular" para ver tu recomendación de carrera.
- Visualiza el resultado en una gráfica de barras y funciones de membresía.

## Licencia
Proyecto educativo para prácticas de sistemas expertos y lógica difusa de la materia de IA.

## Autores
- Mateo Berrío Cardona
- Mariana Montoya Sepúlveda
