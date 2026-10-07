import json
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ARCHIVO_TUTORES = DATA_DIR / "tutores.json"
ARCHIVO_SOLICITUDES = DATA_DIR / "solicitudes.json"

MATERIAS = [
    "Python",
    "Java",
    "Bases de Datos",
    "Inglés",
    "Desarrollo Web",
    "Matemáticas",
]

HORARIOS = ["Mañana", "Tarde", "Noche"]
NIVELES = ["Básico", "Intermedio", "Avanzado"]

TUTORES_INICIALES = [
    {
        "id": 1,
        "nombre": "Laura Gómez",
        "materias": ["Python", "Bases de Datos"],
        "horarios": ["Tarde", "Noche"],
        "anios_experiencia": 4,
        "nivel": "Avanzado",
    },
    {
        "id": 2,
        "nombre": "Carlos Ruiz",
        "materias": ["Java", "Desarrollo Web"],
        "horarios": ["Mañana", "Tarde"],
        "anios_experiencia": 3,
        "nivel": "Intermedio",
    },
    {
        "id": 3,
        "nombre": "Ana Martínez",
        "materias": ["Inglés", "Matemáticas"],
        "horarios": ["Mañana", "Noche"],
        "anios_experiencia": 5,
        "nivel": "Avanzado",
    },
    {
        "id": 4,
        "nombre": "Miguel Torres",
        "materias": ["Python", "Desarrollo Web"],
        "horarios": ["Mañana"],
        "anios_experiencia": 2,
        "nivel": "Intermedio",
    },
    {
        "id": 5,
        "nombre": "Sofía Ramírez",
        "materias": ["Bases de Datos", "Python"],
        "horarios": ["Noche"],
        "anios_experiencia": 6,
        "nivel": "Avanzado",
    },
    {
        "id": 6,
        "nombre": "Daniel Castro",
        "materias": ["Matemáticas", "Java"],
        "horarios": ["Tarde", "Noche"],
        "anios_experiencia": 1,
        "nivel": "Básico",
    },
]


def guardar_json(ruta, datos):
    """Guarda una lista en un archivo JSON con caracteres en español."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=4)


def cargar_json(ruta):
    """Lee un archivo JSON. Si está vacío o dañado, devuelve una lista vacía."""
    try:
        with ruta.open("r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
            return datos if isinstance(datos, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def inicializar_archivos():
    """Crea los archivos de datos la primera vez que se ejecuta el proyecto."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not ARCHIVO_TUTORES.exists():
        guardar_json(ARCHIVO_TUTORES, TUTORES_INICIALES)
    if not ARCHIVO_SOLICITUDES.exists():
        guardar_json(ARCHIVO_SOLICITUDES, [])


def cargar_tutores():
    inicializar_archivos()
    return cargar_json(ARCHIVO_TUTORES)


def cargar_solicitudes():
    inicializar_archivos()
    return cargar_json(ARCHIVO_SOLICITUDES)


def siguiente_id(registros):
    if not registros:
        return 1
    return max(registro.get("id", 0) for registro in registros) + 1


def registrar_tutor(tutor):
    tutores = cargar_tutores()
    tutor["id"] = siguiente_id(tutores)
    tutores.append(tutor)
    guardar_json(ARCHIVO_TUTORES, tutores)


def eliminar_tutor(tutor_id):
    """Elimina un tutor por su identificador y devuelve True si lo encontró."""
    tutores = cargar_tutores()
    tutores_actualizados = [
        tutor for tutor in tutores if tutor.get("id") != tutor_id
    ]

    if len(tutores_actualizados) == len(tutores):
        return False

    guardar_json(ARCHIVO_TUTORES, tutores_actualizados)
    return True


def registrar_solicitud(solicitud, recomendados, puntaje_maximo):
    solicitudes = cargar_solicitudes()
    solicitud_guardada = solicitud.copy()
    solicitud_guardada["id"] = siguiente_id(solicitudes)
    solicitud_guardada["fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    solicitud_guardada["tutores_recomendados"] = recomendados
    solicitud_guardada["puntaje_maximo"] = puntaje_maximo
    solicitudes.append(solicitud_guardada)
    guardar_json(ARCHIVO_SOLICITUDES, solicitudes)


def puntos_por_experiencia(anios):
    """Cada año vale 4 puntos, hasta un máximo de 20."""
    return min(max(int(anios), 0) * 4, 20)


def texto_normalizado(texto):
    return str(texto).strip().casefold()


def tutor_domina_materia(tutor, materia):
    materia_buscada = texto_normalizado(materia)
    return any(
        texto_normalizado(materia_tutor) == materia_buscada
        for materia_tutor in tutor.get("materias", [])
    )


def calcular_compatibilidad(tutor, solicitud):
    """Calcula el puntaje y los motivos de un tutor para una solicitud."""
    materia = solicitud["materia"]
    horario = solicitud["horario"]
    puntaje = 0
    justificacion = []

    if tutor_domina_materia(tutor, materia):
        puntaje += 50
        justificacion.append(f"Domina {materia}.")
    else:
        return None

    horarios_normalizados = [
        texto_normalizado(item) for item in tutor.get("horarios", [])
    ]
    if texto_normalizado(horario) in horarios_normalizados:
        puntaje += 30
        justificacion.append(f"Tiene disponibilidad en la {horario.lower()}.")

    anios = int(tutor.get("anios_experiencia", 0))
    puntos_experiencia = puntos_por_experiencia(anios)
    puntaje += puntos_experiencia
    if anios > 0:
        palabra_anio = "año" if anios == 1 else "años"
        justificacion.append(
            f"Cuenta con {anios} {palabra_anio} de experiencia "
            f"(+{puntos_experiencia} puntos)."
        )

    if tutor.get("nivel") == solicitud.get("nivel_preferido"):
        justificacion.append(
            f"Su nivel {tutor['nivel']} coincide con la preferencia del estudiante."
        )

    return {
        "tutor": tutor,
        "puntaje": puntaje,
        "justificacion": justificacion,
    }


def buscar_tutores_compatibles(tutores, solicitud):
    """Devuelve resultados ordenados y el ganador o los ganadores del empate."""
    resultados = []

    for tutor in tutores:
        resultado = calcular_compatibilidad(tutor, solicitud)
        if resultado is not None:
            resultados.append(resultado)

    resultados.sort(
        key=lambda item: (
            -item["puntaje"],
            -int(item["tutor"].get("anios_experiencia", 0)),
            texto_normalizado(item["tutor"].get("nombre", "")),
        )
    )

    if not resultados:
        return [], []

    mayor_puntaje = resultados[0]["puntaje"]
    empatados_por_puntaje = [
        item for item in resultados if item["puntaje"] == mayor_puntaje
    ]
    mayor_experiencia = max(
        int(item["tutor"].get("anios_experiencia", 0))
        for item in empatados_por_puntaje
    )
    ganadores = [
        item
        for item in empatados_por_puntaje
        if int(item["tutor"].get("anios_experiencia", 0)) == mayor_experiencia
    ]

    return resultados, ganadores

