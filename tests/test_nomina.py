"""Pruebas unitarias para validar las reglas de negocio del sistema de nómina."""
import unittest
from src.modelos import (
    EmpleadoAsalariado,
    EmpleadoPorHoras,
    EmpleadoPorComision,
    EmpleadoTemporal,
    BusinessRuleException
)
from src.servicios import ServicioLiquidacionNomina


class TestSistemaNomina(unittest.TestCase):

    def setUp(self):
        self.servicio = ServicioLiquidacionNomina()

    def test_asalariado_bono_antiguedad_y_alimentacion(self):
        emp = EmpleadoAsalariado("A1", "Carlos", anios_antiguedad=6, salario_fijo=2_000_000)
        self.assertEqual(emp.calcular_salario_bruto(), 2_200_000)
        self.assertEqual(emp.calcular_beneficios_empresa(), 1_000_000)

    def test_horas_extras_y_fondo_ahorro(self):
        # 50 hrs: 40 normales a 10.000 + 10 extras a 15.000 = 550.000
        emp = EmpleadoPorHoras("H1", "Ana", anios_antiguedad=2, horas_trabajadas=50,
                               tarifa_hora=10_000, acepta_fondo_ahorro=True)
        self.assertEqual(emp.calcular_salario_bruto(), 550_000)
        # Deducción 2% sobre el salario bruto
        self.assertEqual(emp.calcular_deducciones_voluntarias(), 11_000)

    def test_comision_meta_superada(self):
        # Ventas > 20M: 5% comisión + 3% bono extra sobre ventas
        emp = EmpleadoPorComision("C1", "Luis", anios_antiguedad=1, salario_base=1_500_000,
                                  porcentaje_comision=0.05, total_ventas=30_000_000)
        self.assertEqual(emp.calcular_salario_bruto(), 3_900_000)
        self.assertEqual(emp.calcular_beneficios_empresa(), 1_000_000)

    def test_empleado_temporal_sin_beneficios(self):
        emp = EmpleadoTemporal("T1", "Sara", anios_antiguedad=0, salario_mensual=1_300_000)
        self.assertEqual(emp.calcular_salario_bruto(), 1_300_000)
        self.assertEqual(emp.calcular_beneficios_empresa(), 0.0)
        self.assertEqual(emp.calcular_deducciones_voluntarias(), 0.0)

    def test_validaciones_de_negocio_excepciones(self):
        with self.assertRaises(BusinessRuleException):
            EmpleadoPorHoras("H2", "Pepe", 1, horas_trabajadas=-2, tarifa_hora=10_000)

        with self.assertRaises(BusinessRuleException):
            EmpleadoPorComision("C2", "Maria", 1, 1_000_000, 0.05, total_ventas=-100)

    def test_servicio_liquidacion_consolidada(self):
        emp1 = EmpleadoTemporal("T1", "Sara", 0, 1_000_000)
        self.servicio.registrar_empleado(emp1)
        resumen = self.servicio.liquidar_todos()
        self.assertEqual(len(resumen), 1)
        self.assertEqual(resumen[0]["id"], "T1")


if __name__ == "__main__":
    unittest.main()