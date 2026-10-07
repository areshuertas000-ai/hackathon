# El tutor perfecto para cada estudiante

Proyecto universitario sencillo desarrollado con Python y Streamlit. Permite
registrar tutores, guardar solicitudes y recomendar el tutor con mayor
compatibilidad mediante un sistema de puntos.

## Funcionalidades

- Registro persistente de tutores en `data/tutores.json`.
- Seis tutores de prueba incluidos.
- Eliminación de tutores con confirmación y guardado inmediato.
- Búsqueda por materia, horario y preferencia de nivel.
- Resultados compatibles ordenados de mayor a menor puntaje.
- Recomendación automática con justificación.
- Desempate por años de experiencia y empate múltiple cuando corresponde.
- Historial persistente en `data/solicitudes.json`.
- Validaciones de los campos obligatorios.

## Cómo ejecutar el proyecto

Abre PowerShell dentro de esta carpeta y ejecuta:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Streamlit mostrará una dirección local, normalmente `http://localhost:8501`.
Ábrela en el navegador.

## Sistema de puntuación

| Criterio | Puntos |
|---|---:|
| Domina la materia | 50 |
| Coincide el horario | 30 |
| Experiencia | 4 por año, máximo 20 |
| **Máximo total** | **100** |

Un tutor que no domina la materia se descarta y nunca puede ganar. Si varios
tutores obtienen el mismo puntaje, gana quien tenga más años de experiencia.
Si también tienen los mismos años, el sistema recomienda a todos los que
continúen empatados.

La preferencia de nivel se guarda y se informa en la justificación cuando
coincide, pero no suma puntos porque la rúbrica indicada asigna los 100 puntos
únicamente a materia, horario y experiencia.

## Ejemplo para la demostración

Busca un tutor con estos datos:

- Estudiante: Valentina
- Materia: Python
- Horario: Tarde
- Nivel preferido: Avanzado

Laura Gómez será recomendada con 96/100: 50 por Python, 30 por el horario de
la tarde y 16 por sus cuatro años de experiencia.

## Estructura

```text
el-tutor-perfecto/
├── app.py                  # Interfaz de Streamlit
├── logica.py               # Archivos JSON y algoritmo de compatibilidad
├── requirements.txt        # Dependencias
├── data/
│   ├── tutores.json        # Tutores guardados
│   └── solicitudes.json    # Historial de búsquedas
├── tests/
│   └── test_logica.py      # Pruebas automáticas del algoritmo
└── .streamlit/
    └── config.toml         # Colores de la interfaz
```

## Cómo explicar el algoritmo

1. La solicitud del estudiante llega con materia y horario.
2. El programa recorre todos los tutores.
3. Si un tutor no domina la materia, se descarta inmediatamente.
4. Los demás reciben 50 puntos por la materia, 30 si coincide el horario y
   hasta 20 por experiencia.
5. Los resultados se ordenan por puntaje y luego por experiencia.
6. El primer resultado es la recomendación; si el empate continúa, se muestran
   las dos o más opciones.

## Ejecutar las pruebas

Desde la carpeta del proyecto:

```powershell
python -m unittest discover -s tests -v
```
