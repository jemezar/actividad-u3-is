"""Script de demostración y ejecución del sistema de nómina."""
from src.modelos import (
    EmpleadoAsalariado,
    EmpleadoPorHoras,
    EmpleadoPorComision,
    EmpleadoTemporal
)
from src.servicios import ServicioLiquidacionNomina


def formatear_moneda(valor: float) -> str:
    return f"${valor:,.2f}"


def main():
    servicio = ServicioLiquidacionNomina()

    # 1. Instanciación de empleados según las reglas del caso de estudio
    asalariado = EmpleadoAsalariado(
        identificacion="CC-101",
        nombre="Laura Gómez",
        anios_antiguedad=6,       # Aplica bono 10% por tener > 5 años
        salario_fijo=3_000_000.0
    )

    horas = EmpleadoPorHoras(
        identificacion="CC-102",
        nombre="Pedro Martínez",
        anios_antiguedad=2,       # Aplica a fondo de ahorro por > 1 año
        horas_trabajadas=48.0,    # 40 normales + 8 extras (x1.5)
        tarifa_hora=20_000.0,
        acepta_fondo_ahorro=True
    )

    comision = EmpleadoPorComision(
        identificacion="CC-103",
        nombre="Sofia Ramirez",
        anios_antiguedad=3,
        salario_base=1_800_000.0,
        porcentaje_comision=0.04,
        total_ventas=25_000_000.0 # Aplica bono adicional del 3% (> $20M)
    )

    temporal = EmpleadoTemporal(
        identificacion="CC-104",
        nombre="Andrés Torres",
        anios_antiguedad=0,
        salario_mensual=1_500_000.0
    )

    # 2. Registro en el servicio
    for emp in [asalariado, horas, comision, temporal]:
        servicio.registrar_empleado(emp)

    # 3. Reporte de nómina
    print("=" * 80)
    print(f"{'REPORTE DE LIQUIDACIÓN DE NÓMINA':^80}")
    print("=" * 80)

    for emp in servicio.liquidar_todos():
        print(f"Empleado: {emp['nombre']} ({emp['id']}) | Tipo: {emp['tipo']}")
        print(f"  (+) Salario Bruto:           {formatear_moneda(emp['salario_bruto'])}")
        print(f"  (+) Beneficios Empresa:      {formatear_moneda(emp['beneficios'])}")
        print(f"  (-) Deducciones Oblig. (ARL/Salud/Pensión): {formatear_moneda(emp['deducciones_obligatorias'])}")
        print(f"  (-) Deducciones Voluntarias: {formatear_moneda(emp['deducciones_voluntarias'])}")
        print(f"  (=) TOTAL NETO A PAGAR:      {formatear_moneda(emp['salario_neto'])}")
        print("-" * 80)

    total_empresa = servicio.calcular_total_nomina_empresa()
    print(f"TOTAL GENERAL NÓMINA EMPRESA: {formatear_moneda(total_empresa)}")
    print("=" * 80)


if __name__ == "__main__":
    main()