"""
Módulo de exportación y reportes contables del sistema de nómina.

Diseñado bajo los principios SOLID:
- S (Single Responsibility): Responsable únicamente de la persistencia y formateo de datos para exportación.
- O (Open/Closed): La clase abstracta ExportadorReporte permite añadir nuevos formatos (JSON, Excel, PDF)
  sin modificar la lógica existente.
- D (Dependency Inversion): Depende de contratos de datos estructurados e interfaces de liquidación.
"""

from abc import ABC, abstractmethod
import csv
from typing import List, Dict, Any


class ExportadorReporte(ABC):
    """Interfaz base para exportadores de liquidación contable."""

    @abstractmethod
    def exportar(self, registros: List[Dict[str, Any]], ruta_destino: str) -> str:
        """
        Exporta los registros de nómina a la ruta especificada.

        :param registros: Lista de diccionarios con la liquidación de cada empleado.
        :param ruta_destino: Ruta del archivo destino.
        :return: Ruta del archivo generado.
        """
        pass


class ExportadorNominaCSV(ExportadorReporte):
    """Exportador especializado en generar reportes en formato CSV estándar delimitado."""

    def __init__(self, delimitador: str = ","):
        self.delimitador = delimitador

    def exportar(self, registros: List[Dict[str, Any]], ruta_destino: str) -> str:
        """
        Genera un archivo CSV con la liquidación detallada de nómina.
        """
        columnas = [
            ("identificacion", "Identificación"),
            ("nombre", "Colaborador"),
            ("cargo_tipo", "Modalidad"),
            ("salario_bruto", "Salario Bruto (COP)"),
            ("beneficio_alimentacion", "Beneficio Alimentación (COP)"),
            ("deducciones_ley", "Deducciones de Ley (COP)"),
            ("deducciones_voluntarias", "Deducciones Voluntarias (COP)"),
            ("salario_neto", "Salario Neto a Pagar (COP)"),
        ]

        with open(ruta_destino, mode="w", newline="", encoding="utf-8") as archivo:
            writer = csv.writer(archivo, delimiter=self.delimitador)
            # Escribir encabezados amigables
            writer.writerow([nombre_col for _, nombre_col in columnas])

            # Escribir filas de datos
            for fila in registros:
                writer.writerow([
                    fila.get(campo, "")
                    for campo, _ in columnas
                ])

        return ruta_destino
