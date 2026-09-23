"""
Suite de Pruebas Unitarias Automatizadas para el Sistema de Nómina.

Valida todas las reglas de negocio descritas en la Actividad Unidad 3:
1. Empleados Asalariados (salario fijo, bono 10% si > 5 años, bono de alimentación).
2. Empleados por Horas (tarifa base, horas extras x1.5 si > 40h, sin bonos, fondo de ahorro 2% si > 1 año y aceptado).
3. Empleados por Comisión (salario base + comisión, bono adicional 3% si ventas > 20M, bono alimentación).
4. Empleados Temporales (salario fijo, sin bonos ni beneficios).
5. Deducciones obligatorias de ley (4% Salud, 4% Pensión, ARL).
6. Validaciones de negocio y excepciones (salario neto negativo, horas negativas, ventas negativas, etc.).
7. Servicio de liquidación contable y consolidación de balances empresariales.
"""

import sys
from pathlib import Path
import unittest

# Asegurar que la raíz del proyecto esté en sys.path para ejecución directa del archivo
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.modelos import (
    Empleado,
    EmpleadoAsalariado,
    EmpleadoPorHoras,
    EmpleadoPorComision,
    EmpleadoTemporal,
    BusinessRuleException,
)
from src.servicios import ServicioLiquidacionNomina


class TestSistemaNomina(unittest.TestCase):
    """Conjunto de casos de prueba unitarios para verificar la integridad del dominio y los servicios."""

    def setUp(self):
        """Instanciación del orquestador contable antes de cada prueba."""
        self.servicio = ServicioLiquidacionNomina()

    # =========================================================================
    # 1. PRUEBAS: EMPLEADO ASALARIADO
    # =========================================================================

    def test_asalariado_bono_antiguedad_mayor_a_5_anios(self):
        """Si tiene más de 5 años (ej. 6 años), recibe bono del 10% sobre el salario fijo."""
        emp = EmpleadoAsalariado("AS-01", "Carlos Gómez", anios_antiguedad=6, salario_fijo=2_000_000.0)
        # Salario fijo (2.000.000) + 10% bono (200.000) = 2.200.000
        self.assertEqual(emp.calcular_salario_bruto(), 2_200_000.0)
        # Bono de alimentación para empleados permanentes
        self.assertEqual(emp.calcular_beneficios_empresa(), 1_000_000.0)

    def test_asalariado_sin_bono_limite_exacto_5_anios(self):
        """Con exactamente 5 años de antigüedad no debe recibir el bono del 10% (debe ser > 5 años)."""
        emp = EmpleadoAsalariado("AS-02", "Marta Pérez", anios_antiguedad=5, salario_fijo=2_000_000.0)
        self.assertEqual(emp.calcular_salario_bruto(), 2_000_000.0)
        self.assertEqual(emp.calcular_bono_antiguedad(), 0.0)

    def test_asalariado_sin_bono_menor_a_5_anios(self):
        """Con 2 años de antigüedad no aplica el bono del 10%."""
        emp = EmpleadoAsalariado("AS-03", "Andrés Marín", anios_antiguedad=2, salario_fijo=3_000_000.0)
        self.assertEqual(emp.calcular_salario_bruto(), 3_000_000.0)

    # =========================================================================
    # 2. PRUEBAS: EMPLEADO POR HORAS
    # =========================================================================

    def test_horas_ordinarias_sin_recargo(self):
        """Si trabaja 40 horas o menos, solo se calcula la tarifa base y no recibe bonos."""
        emp = EmpleadoPorHoras("HR-01", "Pedro López", anios_antiguedad=2, horas_trabajadas=40.0, tarifa_hora=10_000.0)
        self.assertEqual(emp.calcular_salario_bruto(), 400_000.0)
        self.assertEqual(emp.calcular_beneficios_empresa(), 0.0)

    def test_horas_extras_recargo_cincuenta_por_ciento(self):
        """Las horas extras (> 40h) se pagan a 1.5 veces la tarifa normal."""
        # 46 horas: 40 normales a $10.000 ($400.000) + 6 extras a $15.000 ($90.000) = $490.000
        emp = EmpleadoPorHoras("HR-02", "Juan Polo", anios_antiguedad=2, horas_trabajadas=46.0, tarifa_hora=10_000.0)
        self.assertEqual(emp.calcular_salario_bruto(), 490_000.0)

    def test_horas_fondo_ahorro_mayor_a_1_anio_y_aceptado(self):
        """Si tiene más de 1 año y acepta el fondo de ahorro, se deduce el 2% del salario bruto."""
        emp = EmpleadoPorHoras("HR-03", "Ana Morales", anios_antiguedad=2, horas_trabajadas=40.0,
                               tarifa_hora=10_000.0, acepta_fondo_ahorro=True)
        # Bruto = 400.000 -> Deducción voluntaria = 400.000 * 0.02 = 8.000
        self.assertEqual(emp.calcular_deducciones_voluntarias(), 8_000.0)

    def test_horas_sin_fondo_ahorro_si_rechaza(self):
        """Si tiene antigüedad mayor a 1 año pero no acepta el fondo, la deducción es 0."""
        emp = EmpleadoPorHoras("HR-04", "Sofía Vargas", anios_antiguedad=3, horas_trabajadas=40.0,
                               tarifa_hora=10_000.0, acepta_fondo_ahorro=False)
        self.assertEqual(emp.calcular_deducciones_voluntarias(), 0.0)

    def test_horas_sin_fondo_ahorro_antiguedad_insuficiente(self):
        """Si tiene 1 año o menos (ej. 1 año exacto), no puede acceder al fondo de ahorro aunque acepte."""
        emp = EmpleadoPorHoras("HR-05", "Diana Ruiz", anios_antiguedad=1, horas_trabajadas=40.0,
                               tarifa_hora=10_000.0, acepta_fondo_ahorro=True)
        self.assertEqual(emp.calcular_deducciones_voluntarias(), 0.0)

    # =========================================================================
    # 3. PRUEBAS: EMPLEADO POR COMISIÓN
    # =========================================================================

    def test_comision_sin_bono_ventas_menores_o_iguales_a_20m(self):
        """Ventas <= $20.000.000: salario base + comisión habitual, sin bono adicional del 3%."""
        # Base: 1.500.000, 5% de 20.000.000 = 1.000.000 -> Total Bruto = 2.500.000
        emp = EmpleadoPorComision("CM-01", "Lucía Díaz", anios_antiguedad=2,
                                  salario_base=1_500_000.0, porcentaje_comision=0.05, total_ventas=20_000_000.0)
        self.assertEqual(emp.calcular_salario_bruto(), 2_500_000.0)
        self.assertEqual(emp.calcular_beneficios_empresa(), 1_000_000.0)

    def test_comision_con_bono_ventas_superiores_a_20m(self):
        """Ventas > $20.000.000: recibe el 3% adicional sobre el total de ventas."""
        # Ventas: 30.000.000. Base: 1.500.000.
        # Comisión 5% = 1.500.000. Bono 3% sobre ventas = 900.000.
        # Total Bruto = 1.500.000 + 1.500.000 + 900.000 = 3.900.000
        emp = EmpleadoPorComision("CM-02", "Roberto Cruz", anios_antiguedad=3,
                                  salario_base=1_500_000.0, porcentaje_comision=0.05, total_ventas=30_000_000.0)
        self.assertEqual(emp.calcular_salario_bruto(), 3_900_000.0)
        self.assertEqual(emp.calcular_beneficios_empresa(), 1_000_000.0)

    # =========================================================================
    # 4. PRUEBAS: EMPLEADO TEMPORAL
    # =========================================================================

    def test_temporal_salario_fijo_sin_beneficios(self):
        """Empleado temporal solo devenga su salario pactado, sin bonos ni alimentación ni fondo de ahorro."""
        emp = EmpleadoTemporal("TM-01", "Felipe Castro", anios_antiguedad=1, salario_mensual=1_400_000.0)
        self.assertEqual(emp.calcular_salario_bruto(), 1_400_000.0)
        self.assertEqual(emp.calcular_beneficios_empresa(), 0.0)
        self.assertEqual(emp.calcular_deducciones_voluntarias(), 0.0)

    # =========================================================================
    # 5. PRUEBAS: DEDUCCIONES OBLIGATORIAS (SALUD, PENSIÓN, ARL)
    # =========================================================================

    def test_deducciones_obligatorias_calculo_exacto(self):
        """Valida que se descuente 4% Salud, 4% Pensión y 0.522% ARL sobre el bruto."""
        emp = EmpleadoTemporal("TM-02", "Esteban Real", anios_antiguedad=0, salario_mensual=1_000_000.0)
        # 1.000.000 * (0.04 + 0.04 + 0.00522) = 1.000.000 * 0.08522 = 85.220
        self.assertAlmostEqual(emp.calcular_deducciones_obligatorias(), 85_220.0, places=2)

    # =========================================================================
    # 6. PRUEBAS: VALIDACIONES DE NEGOCIO Y EXCEPCIONES
    # =========================================================================

    def test_validacion_horas_negativas_lanza_excepcion(self):
        """No se permiten horas laboradas con valores negativos."""
        with self.assertRaises(BusinessRuleException):
            EmpleadoPorHoras("HR-ERR", "Error", 1, horas_trabajadas=-5.0, tarifa_hora=10_000.0)

    def test_validacion_tarifa_hora_invalida(self):
        """Tarifa por hora menor o igual a cero debe lanzar excepción."""
        with self.assertRaises(BusinessRuleException):
            EmpleadoPorHoras("HR-ERR", "Error", 1, horas_trabajadas=40.0, tarifa_hora=0.0)

    def test_validacion_ventas_negativas_lanza_excepcion(self):
        """Las ventas en empleado por comisión no pueden ser menores a $0."""
        with self.assertRaises(BusinessRuleException):
            EmpleadoPorComision("CM-ERR", "Error", 1, salario_base=1_000_000.0,
                                porcentaje_comision=0.05, total_ventas=-100.0)

    def test_validacion_antiguedad_negativa(self):
        """Antigüedad menor a 0 debe lanzar BusinessRuleException."""
        with self.assertRaises(BusinessRuleException):
            EmpleadoTemporal("TM-ERR", "Error", anios_antiguedad=-1, salario_mensual=1_000_000.0)

    def test_validacion_campos_vacios(self):
        """Identificación o nombre vacíos deben ser rechazados."""
        with self.assertRaises(BusinessRuleException):
            EmpleadoTemporal("", "Nombre Válido", 0, 1_000_000.0)
        with self.assertRaises(BusinessRuleException):
            EmpleadoTemporal("CC-1", "   ", 0, 1_000_000.0)

    # =========================================================================
    # 7. PRUEBAS: SERVICIO DE LIQUIDACIÓN Y REPORTE
    # =========================================================================

    def test_servicio_liquidacion_consolidado_y_totales(self):
        """Verifica que el servicio registre colaboradores y calcule correctamente los agregados."""
        e1 = EmpleadoAsalariado("AS-1", "Carlos", 6, 2_000_000.0)
        e2 = EmpleadoTemporal("TM-1", "Ana", 0, 1_000_000.0)

        self.servicio.agregar_empleado(e1)
        self.servicio.agregar_empleado(e2)

        reporte = self.servicio.generar_reporte_consolidado()
        self.assertEqual(len(reporte), 2)

        totales = self.servicio.calcular_totales_empresa()
        self.assertGreater(totales["total_salario_bruto"], 0)
        self.assertGreater(totales["total_beneficios_empresa"], 0)
    # =========================================================================
    # 8. PRUEBAS: EXPORTADOR DE REPORTES (CSV)
    # =========================================================================

    def test_exportador_nomina_csv(self):
        """Verifica la generación y contenido correcto del archivo CSV de nómina."""
        import tempfile
        import os

        e1 = EmpleadoAsalariado("AS-1", "Carlos Gómez", 6, 2_000_000.0)
        self.servicio.agregar_empleado(e1)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            temp_path = temp_file.name

        try:
            ruta_generada = self.servicio.exportar_reporte(temp_path)
            self.assertTrue(os.path.exists(ruta_generada))

            with open(ruta_generada, mode="r", encoding="utf-8") as f:
                lineas = f.readlines()
                self.assertGreaterEqual(len(lineas), 2)  # Encabezado + al menos 1 fila
                self.assertIn("Identificación", lineas[0])
                self.assertIn("AS-1", lineas[1])
                self.assertIn("Carlos Gómez", lineas[1])
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()