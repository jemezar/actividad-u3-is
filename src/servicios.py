"""
Módulo de servicios: Procesamiento y Liquidación Contable de Nómina.

Este módulo implementa el orquestador contable que procesa colecciones de empleados,
calcula las liquidaciones individuales y consolida las cifras para el balance empresarial.
Cumple con el principio de Inversión de Dependencias (DIP) al operar sobre la abstracción Empleado
y delegar la persistencia en abstracciones ExportadorReporte.
"""

from typing import List, Dict, Any, Optional
from src.modelos import Empleado
from src.exportadores import ExportadorReporte, ExportadorNominaCSV


class ServicioLiquidacionNomina:
    """
    Servicio encargado de liquidar y consolidar la nómina empresarial.
    Permite registrar colaboradores, generar balances y exportar reportes analíticos de nómina.
    """

    def __init__(self):
        self._nomina: List[Empleado] = []

    def agregar_empleado(self, empleado: Empleado) -> None:
        """Registra un empleado en el sistema de nómina."""
        self._nomina.append(empleado)

    # Alias para compatibilidad con llamadas existentes
    registrar_empleado = agregar_empleado

    @property
    def empleados(self) -> List[Empleado]:
        """Retorna una copia superficial de la lista de empleados registrados."""
        return list(self._nomina)

    def liquidar_empleado(self, empleado: Empleado) -> Dict[str, Any]:
        """
        Calcula el desglose financiero individual de un empleado.
        
        :param empleado: Instancia de una subclase de Empleado.
        :return: Diccionario estructurado con los rubros devengados y deducidos.
        """
        salario_bruto = empleado.calcular_salario_bruto()
        beneficios = empleado.calcular_beneficios_empresa()
        deducciones_ley = empleado.calcular_deducciones_obligatorias()
        deducciones_vol = empleado.calcular_deducciones_voluntarias()
        salario_neto = empleado.calcular_salario_neto()

        return {
            "identificacion": empleado.identificacion,
            "id": empleado.identificacion,  # retrocompatibilidad
            "nombre": empleado.nombre,
            "cargo_tipo": empleado.__class__.__name__,
            "tipo": empleado.__class__.__name__,  # retrocompatibilidad
            "anios_antiguedad": empleado.anios_antiguedad,
            "salario_bruto": salario_bruto,
            "beneficio_alimentacion": beneficios,
            "beneficios": beneficios,  # retrocompatibilidad
            "deducciones_ley": deducciones_ley,
            "deducciones_obligatorias": deducciones_ley,  # retrocompatibilidad
            "deducciones_voluntarias": deducciones_vol,
            "salario_neto": salario_neto,
        }

    def generar_reporte_consolidado(self) -> List[Dict[str, Any]]:
        """Genera el reporte detallado de nómina para todos los empleados vinculados."""
        return [self.liquidar_empleado(emp) for emp in self._nomina]

    # Alias para compatibilidad
    liquidar_todos = generar_reporte_consolidado

    def calcular_totales_empresa(self) -> Dict[str, float]:
        """
        Consolida las cifras globales de nómina que asume la empresa:
        - Total Devengado Bruto
        - Total Beneficios Empresa (ej. alimentación)
        - Total Descuentos de Ley (Salud, Pensión, ARL)
        - Total Descuentos Voluntarios (ej. Fondo de Ahorro)
        - Total Desembolso Neto a Trabajadores
        """
        total_bruto = sum(emp.calcular_salario_bruto() for emp in self._nomina)
        total_beneficios = sum(emp.calcular_beneficios_empresa() for emp in self._nomina)
        total_deducciones_ley = sum(emp.calcular_deducciones_obligatorias() for emp in self._nomina)
        total_deducciones_vol = sum(emp.calcular_deducciones_voluntarias() for emp in self._nomina)
        total_neto = sum(emp.calcular_salario_neto() for emp in self._nomina)

        return {
            "total_salario_bruto": total_bruto,
            "total_beneficios_empresa": total_beneficios,
            "total_deducciones_ley": total_deducciones_ley,
            "total_deducciones_voluntarias": total_deducciones_vol,
            "total_salario_neto": total_neto,
        }

    def calcular_gran_total_neto(self) -> float:
        """Calcula el desembolso total de nómina neta por parte de la empresa."""
        return sum(emp.calcular_salario_neto() for emp in self._nomina)

    # Alias para compatibilidad
    calcular_total_nomina_empresa = calcular_gran_total_neto

    def exportar_reporte(self, ruta_destino: str, exportador: Optional[ExportadorReporte] = None) -> str:
        """
        Exporta el reporte consolidado de nómina utilizando la estrategia de exportación indicada.
        Aplica Inversión de Dependencias (DIP) y Abierto/Cerrado (OCP).
        
        :param ruta_destino: Archivo de salida (ej. 'reporte_nomina.csv').
        :param exportador: Instancia de ExportadorReporte. Por defecto usa ExportadorNominaCSV.
        :return: Ruta del archivo generado.
        """
        if exportador is None:
            exportador = ExportadorNominaCSV()
        registros = self.generar_reporte_consolidado()
        return exportador.exportar(registros, ruta_destino)