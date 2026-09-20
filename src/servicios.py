"""Módulo de servicios para el procesamiento y reporte de nómina."""
from typing import List, Dict, Any
from src.modelos import Empleado


class ServicioLiquidacionNomina:
    """Gestiona el cálculo masivo y la generación de reportes contables."""

    def __init__(self):
        self._empleados: List[Empleado] = []

    def registrar_empleado(self, empleado: Empleado) -> None:
        """Registra un empleado en el sistema de nómina."""
        self._empleados.append(empleado)

    def liquidar_empleado(self, empleado: Empleado) -> Dict[str, Any]:
        """Genera el desglose contable individual de un empleado."""
        return {
            "id": empleado.identificacion,
            "nombre": empleado.nombre,
            "tipo": empleado.__class__.__name__,
            "salario_bruto": empleado.calcular_salario_bruto(),
            "beneficios": empleado.calcular_beneficios_empresa(),
            "deducciones_obligatorias": empleado.calcular_deducciones_obligatorias(),
            "deducciones_voluntarias": empleado.calcular_deducciones_voluntarias(),
            "salario_neto": empleado.calcular_salario_neto()
        }

    def liquidar_todos(self) -> List[Dict[str, Any]]:
        """Liquida a todos los empleados registrados."""
        return [self.liquidar_empleado(emp) for emp in self._empleados]

    def calcular_total_nomina_empresa(self) -> float:
        """Calcula el desembolso total de nómina neta por parte de la empresa."""
        return sum(emp.calcular_salario_neto() for emp in self._empleados)