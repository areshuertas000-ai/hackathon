import pandas as pd
import streamlit as st

from logica import (
    HORARIOS,
    MATERIAS,
    NIVELES,
    buscar_tutores_compatibles,
    cargar_solicitudes,
    cargar_tutores,
    eliminar_tutor,
    inicializar_archivos,
    registrar_solicitud,
    registrar_tutor,
)


st.set_page_config(
    page_title="El tutor perfecto",
    page_icon="🎓",
    layout="wide",
)

inicializar_archivos()


def tabla_tutores(tutores):
    filas = []
    for tutor in tutores:
        filas.append(
            {
                "Nombre": tutor["nombre"],
                "Materias": ", ".join(tutor["materias"]),
                "Horarios": ", ".join(tutor["horarios"]),
                "Experiencia": f"{tutor['anios_experiencia']} años",
                "Nivel": tutor["nivel"],
            }
        )
    return pd.DataFrame(filas)


def tabla_resultados(resultados, solicitud):
    filas = []
    for resultado in resultados:
        tutor = resultado["tutor"]
        filas.append(
            {
                "Nombre": tutor["nombre"],
                "Materia": solicitud["materia"],
                "Horarios": ", ".join(tutor["horarios"]),
                "Experiencia": f"{tutor['anios_experiencia']} años",
                "Nivel": tutor["nivel"],
                "Puntaje": f"{resultado['puntaje']}/100",
            }
        )
    return pd.DataFrame(filas)


def mostrar_recomendacion(ganadores):
    if len(ganadores) == 1:
        ganador = ganadores[0]
        st.success(
            f"🏆 Tutor recomendado: {ganador['tutor']['nombre']}  \n"
            f"Compatibilidad: {ganador['puntaje']}/100"
        )
    else:
        nombres = " y ".join(item["tutor"]["nombre"] for item in ganadores)
        st.success(
            f"🏆 Tutores recomendados: {nombres}  \n"
            f"Compatibilidad: {ganadores[0]['puntaje']}/100"
        )
        st.info(
            "Los tutores continúan empatados después de comparar puntaje y años "
            "de experiencia, por eso ambos son buenas opciones."
        )

    st.subheader("Justificación")
    for ganador in ganadores:
        if len(ganadores) > 1:
            st.markdown(f"**{ganador['tutor']['nombre']}**")
        for motivo in ganador["justificacion"]:
            st.markdown(f"- {motivo}")


st.sidebar.title("🎓 Menú")
pagina = st.sidebar.radio(
    "Ir a",
    [
        "Inicio",
        "Registrar tutor",
        "Buscar tutor",
        "Ver tutores",
        "Historial de solicitudes",
    ],
)
st.sidebar.caption("Proyecto universitario desarrollado con Python y Streamlit.")


if pagina == "Inicio":
    st.title("El tutor perfecto para cada estudiante")
    st.header("Encuentra apoyo académico de forma sencilla")
    st.write(
        "Este sistema registra tutores, recibe solicitudes de estudiantes y "
        "recomienda automáticamente la opción con mayor compatibilidad."
    )
    st.info(
        "El puntaje se calcula con tres criterios: materia (50 puntos), "
        "horario (30 puntos) y experiencia (hasta 20 puntos). Un tutor que no "
        "domina la materia nunca puede ser recomendado."
    )

    tutores = cargar_tutores()
    st.subheader("Resumen del sistema")
    columna_1, columna_2, columna_3 = st.columns(3)
    columna_1.metric("Tutores registrados", len(tutores))
    columna_2.metric("Materias disponibles", len(MATERIAS))
    columna_3.metric("Puntaje máximo", "100")

    if st.button("Ver resumen de tutores"):
        st.dataframe(tabla_tutores(tutores), width="stretch", hide_index=True)


elif pagina == "Registrar tutor":
    st.title("Registrar tutor")
    st.write("Completa los datos para agregar un nuevo tutor al sistema.")

    with st.form("formulario_tutor", clear_on_submit=True):
        nombre = st.text_input("Nombre completo")
        materias = st.multiselect("Materias que domina", MATERIAS)
        horarios = st.multiselect("Horarios disponibles", HORARIOS)
        experiencia = st.number_input(
            "Años de experiencia", min_value=0, max_value=50, step=1
        )
        nivel = st.selectbox(
            "Nivel de experiencia",
            NIVELES,
            index=None,
            placeholder="Selecciona un nivel",
        )
        guardar = st.form_submit_button("Registrar tutor")

    if guardar:
        errores = []
        if not nombre.strip():
            errores.append("El nombre no puede estar vacío.")
        if not materias:
            errores.append("Selecciona al menos una materia.")
        if not horarios:
            errores.append("Selecciona al menos un horario.")
        if experiencia < 0:
            errores.append("La experiencia no puede ser negativa.")
        if nivel is None:
            errores.append("Selecciona el nivel de experiencia.")

        if errores:
            for error in errores:
                st.error(error)
        else:
            registrar_tutor(
                {
                    "nombre": nombre.strip(),
                    "materias": materias,
                    "horarios": horarios,
                    "anios_experiencia": int(experiencia),
                    "nivel": nivel,
                }
            )
            st.success(f"El tutor {nombre.strip()} fue registrado correctamente.")

    st.subheader("Tutores registrados")
    st.dataframe(tabla_tutores(cargar_tutores()), width="stretch", hide_index=True)


elif pagina == "Buscar tutor":
    st.title("Buscar el mejor tutor")
    st.write("Ingresa la necesidad del estudiante para calcular la compatibilidad.")

    with st.form("formulario_solicitud"):
        nombre_estudiante = st.text_input("Nombre del estudiante")
        materia = st.selectbox(
            "Materia en la que necesita ayuda",
            MATERIAS,
            index=None,
            placeholder="Selecciona una materia",
        )
        horario = st.selectbox(
            "Horario disponible",
            HORARIOS,
            index=None,
            placeholder="Selecciona un horario",
        )
        nivel_preferido = st.selectbox(
            "Preferencia de nivel del tutor",
            NIVELES,
            index=None,
            placeholder="Selecciona un nivel",
        )
        buscar = st.form_submit_button("Buscar mejor tutor")

    st.caption(
        "La preferencia de nivel se registra y se muestra como información "
        "adicional. No suma puntos porque la rúbrica sólo asigna puntaje a "
        "materia, horario y experiencia."
    )

    if buscar:
        errores = []
        if not nombre_estudiante.strip():
            errores.append("El nombre del estudiante no puede estar vacío.")
        if materia is None:
            errores.append("Selecciona la materia en la que necesita ayuda.")
        if horario is None:
            errores.append("Selecciona el horario disponible.")
        if nivel_preferido is None:
            errores.append("Selecciona la preferencia de nivel del tutor.")

        if errores:
            for error in errores:
                st.error(error)
        else:
            solicitud = {
                "nombre_estudiante": nombre_estudiante.strip(),
                "materia": materia,
                "horario": horario,
                "nivel_preferido": nivel_preferido,
            }
            resultados, ganadores = buscar_tutores_compatibles(
                cargar_tutores(), solicitud
            )

            nombres_ganadores = [
                ganador["tutor"]["nombre"] for ganador in ganadores
            ]
            puntaje_maximo = ganadores[0]["puntaje"] if ganadores else 0
            registrar_solicitud(
                solicitud,
                nombres_ganadores,
                puntaje_maximo,
            )

            if not resultados:
                st.info(
                    f"No hay tutores registrados que dominen {materia}. "
                    "La solicitud quedó guardada en el historial."
                )
            else:
                st.header("Resultados")
                st.dataframe(
                    tabla_resultados(resultados, solicitud),
                    width="stretch",
                    hide_index=True,
                )
                mostrar_recomendacion(ganadores)


elif pagina == "Ver tutores":
    st.title("Tutores registrados")
    tutores = cargar_tutores()

    if tutores:
        st.subheader("Eliminar tutor")
        st.warning(
            "Esta acción elimina al tutor del archivo JSON y no se puede deshacer."
        )

        tutores_por_id = {tutor["id"]: tutor for tutor in tutores}
        tutor_id = st.selectbox(
            "Tutor que deseas eliminar",
            options=list(tutores_por_id.keys()),
            index=None,
            placeholder="Selecciona un tutor",
            format_func=lambda identificador: tutores_por_id[identificador]["nombre"],
        )
        confirmar = st.checkbox("Confirmo que deseo eliminar este tutor")

        if st.button("Eliminar tutor", type="primary"):
            if tutor_id is None:
                st.error("Selecciona el tutor que deseas eliminar.")
            elif not confirmar:
                st.error("Debes confirmar la eliminación.")
            else:
                nombre_eliminado = tutores_por_id[tutor_id]["nombre"]
                if eliminar_tutor(tutor_id):
                    st.success(f"El tutor {nombre_eliminado} fue eliminado.")
                    tutores = cargar_tutores()
                else:
                    st.error("No se encontró el tutor seleccionado.")

        st.subheader("Listado de tutores")
        if tutores:
            st.dataframe(tabla_tutores(tutores), width="stretch", hide_index=True)
            st.info(f"Hay {len(tutores)} tutores registrados en el sistema.")
        else:
            st.info("Ya no hay tutores registrados.")
    else:
        st.info("Todavía no hay tutores registrados.")


elif pagina == "Historial de solicitudes":
    st.title("Historial de solicitudes")
    solicitudes = cargar_solicitudes()

    if solicitudes:
        filas = []
        for solicitud in reversed(solicitudes):
            recomendados = solicitud.get("tutores_recomendados", [])
            filas.append(
                {
                    "Fecha": solicitud.get("fecha", ""),
                    "Estudiante": solicitud["nombre_estudiante"],
                    "Materia": solicitud["materia"],
                    "Horario": solicitud["horario"],
                    "Nivel preferido": solicitud["nivel_preferido"],
                    "Tutor recomendado": ", ".join(recomendados)
                    if recomendados
                    else "Sin coincidencias",
                    "Puntaje": f"{solicitud.get('puntaje_maximo', 0)}/100",
                }
            )
        st.dataframe(pd.DataFrame(filas), width="stretch", hide_index=True)
    else:
        st.info("Aún no se han realizado búsquedas de tutores.")

