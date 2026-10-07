import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from logica import (
    buscar_tutores_compatibles,
    calcular_compatibilidad,
    cargar_json,
    eliminar_tutor,
    guardar_json,
    puntos_por_experiencia,
)


class PruebasCompatibilidad(unittest.TestCase):
    def setUp(self):
        self.solicitud = {
            "nombre_estudiante": "Valentina",
            "materia": "Python",
            "horario": "Tarde",
            "nivel_preferido": "Avanzado",
        }

    def crear_tutor(self, nombre, materias, horarios, anios, nivel="Avanzado"):
        return {
            "nombre": nombre,
            "materias": materias,
            "horarios": horarios,
            "anios_experiencia": anios,
            "nivel": nivel,
        }

    def test_puntos_de_experiencia_tienen_maximo_de_20(self):
        self.assertEqual(puntos_por_experiencia(1), 4)
        self.assertEqual(puntos_por_experiencia(4), 16)
        self.assertEqual(puntos_por_experiencia(5), 20)
        self.assertEqual(puntos_por_experiencia(10), 20)

    def test_puntaje_completo(self):
        tutor = self.crear_tutor("Laura", ["Python"], ["Tarde"], 5)
        resultado = calcular_compatibilidad(tutor, self.solicitud)
        self.assertEqual(resultado["puntaje"], 100)

    def test_tutor_sin_materia_no_es_compatible(self):
        tutor = self.crear_tutor("Carlos", ["Java"], ["Tarde"], 10)
        self.assertIsNone(calcular_compatibilidad(tutor, self.solicitud))

    def test_mayor_experiencia_rompe_empate_de_puntaje(self):
        tutor_5 = self.crear_tutor("Tutor cinco", ["Python"], ["Tarde"], 5)
        tutor_8 = self.crear_tutor("Tutor ocho", ["Python"], ["Tarde"], 8)
        _, ganadores = buscar_tutores_compatibles(
            [tutor_5, tutor_8], self.solicitud
        )
        self.assertEqual([item["tutor"]["nombre"] for item in ganadores], ["Tutor ocho"])

    def test_empate_total_devuelve_dos_ganadores(self):
        tutor_a = self.crear_tutor("Andrea", ["Python"], ["Tarde"], 5)
        tutor_b = self.crear_tutor("Beatriz", ["Python"], ["Tarde"], 5)
        _, ganadores = buscar_tutores_compatibles(
            [tutor_a, tutor_b], self.solicitud
        )
        self.assertEqual(len(ganadores), 2)

    def test_eliminar_tutor_actualiza_el_archivo_json(self):
        with TemporaryDirectory() as carpeta_temporal:
            archivo = Path(carpeta_temporal) / "tutores.json"
            guardar_json(
                archivo,
                [
                    {"id": 1, "nombre": "Laura"},
                    {"id": 2, "nombre": "Carlos"},
                ],
            )

            with patch("logica.ARCHIVO_TUTORES", archivo), patch(
                "logica.inicializar_archivos"
            ):
                self.assertTrue(eliminar_tutor(1))
                self.assertEqual(cargar_json(archivo), [{"id": 2, "nombre": "Carlos"}])
                self.assertFalse(eliminar_tutor(99))


if __name__ == "__main__":
    unittest.main()

