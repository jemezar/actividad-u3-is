"""
Script principal de demostración y ejecución del sistema de liquidación de nómina.

Permite simular el procesamiento mensual de salarios para una empresa con
diversas modalidades contractuales, validando los devengos, beneficios corporativos,
deducciones de ley y voluntarias, y consolidando el balance total a desembolsar.
"""

from src.modelos import (
    EmpleadoAsalariado,
    EmpleadoPorHoras,
    EmpleadoPorComision,
    EmpleadoTemporal,
    BusinessRuleException
)
from src.servicios import ServicioLiquidacionNomina


def formato_cop(valor: float) -> str:
    """Formatea una cantidad monetaria con signo de pesos y separadores de miles."""
    return f"${valor:,.2f}"


def imprimir_encabezado():
    """Imprime el banner institucional de la empresa."""
    print("=" * 95)
    print(f"{'SISTEMA DE LIQUIDACIÓN DE NÓMINA EMPRESARIAL':^95}")
    print(f"{'Universidad de Cartagena - Ingeniería de Software (CIPA 404 Not Found)':^95}")
    print("=" * 95)


def imprimir_reporte_empleados(servicio: ServicioLiquidacionNomina):
    """Muestra el reporte detallado por cada trabajador registrado."""
    reporte = servicio.generar_reporte_consolidado()

    print(f"{'ID':<10} | {'COLABORADOR':<20} | {'MODALIDAD':<22} | {'BRUTO':>12} | {'BENEFICIOS':>12} | {'DED. LEY':>11} | {'DED. VOL':>11} | {'NETO':>12}")
    print("-" * 128)

    for item in reporte:
        print(
            f"{item['identificacion']:<10} | "
            f"{item['nombre']:<20} | "
            f"{item['cargo_tipo']:<22} | "
            f"{formato_cop(item['salario_bruto']):>12} | "
            f"{formato_cop(item['beneficio_alimentacion']):>12} | "
            f"{formato_cop(item['deducciones_ley']):>11} | "
            f"{formato_cop(item['deducciones_voluntarias']):>11} | "
            f"{formato_cop(item['salario_neto']):>12}"
        )
    print("-" * 128)


def imprimir_balance_empresarial(servicio: ServicioLiquidacionNomina):
    """Presenta el consolidado financiero de desembolsos y retenciones."""
    totales = servicio.calcular_totales_empresa()

    print("\n" + "=" * 60)
    print(f"{'BALANCE Y TOTALES CONSOLIDADOS DE NÓMINA':^60}")
    print("=" * 60)
    print(f" (+) Total Salarios Brutos Devengados:   {formato_cop(totales['total_salario_bruto']):>18}")
    print(f" (+) Total Beneficios Alimentación:      {formato_cop(totales['total_beneficios_empresa']):>18}")
    print(f" (-) Total Retenciones Ley (Salud/ARL):  {formato_cop(totales['total_deducciones_ley']):>18}")
    print(f" (-) Total Ahorro Voluntario Retenido:   {formato_cop(totales['total_deducciones_voluntarias']):>18}")
    print("-" * 60)
    print(f" (=) GRAN TOTAL NÓMINA NETA A DISPERSAR: {formato_cop(totales['total_salario_neto']):>18}")
    print("=" * 60 + "\n")


def main():
    """Punto de entrada de la aplicación."""
    servicio = ServicioLiquidacionNomina()

    imprimir_encabezado()

    # 1. Creación de casos representativos de cada tipo de empleado
    print("\n[+] Registrando empleados en la plataforma de nómina...")
    
    # Caso 1: Asalariado con más de 5 años (recibe bono antigüedad 10% + bono alimentación)
    emp_asalariado = EmpleadoAsalariado(
        identificacion="ASAL-001",
        nombre="Jorge Meza",
        anios_antiguedad=6,
        salario_fijo=3_500_000.0
    )

    # Caso 2: Empleado por Horas con horas extras (> 40h) y ahorro voluntario activo (> 1 año)
    emp_horas = EmpleadoPorHoras(
        identificacion="HORAS-002",
        nombre="Juan Assia",
        anios_antiguedad=2,
        horas_trabajadas=48.0,   # 40 horas base + 8 horas extras con recargo del 50%
        tarifa_hora=25_000.0,
        acepta_fondo_ahorro=True # Descuento del 2% del salario bruto
    )

    # Caso 3: Empleado por Comisión con ventas superiores a $20M (recibe bono adicional 3% + alimentación)
    emp_comision = EmpleadoPorComision(
        identificacion="COMIS-003",
        nombre="Yaismer Figueroa",
        anios_antiguedad=3,
        salario_base=2_000_000.0,
        porcentaje_comision=0.05,     # 5% de comisión
        total_ventas=28_000_000.0     # Supera meta: bono adicional 3%
    )

    # Caso 4: Empleado Temporal a término fijo (sin bonos ni beneficios)
    emp_temporal = EmpleadoTemporal(
        identificacion="TEMP-004",
        nombre="Juan Hernandez",
        anios_antiguedad=1,
        salario_mensual=1_800_000.0
    )

    # Registrar en el servicio
    for emp in [emp_asalariado, emp_horas, emp_comision, emp_temporal]:
        servicio.agregar_empleado(emp)

    print(f"[OK] Se registraron exitosamente {len(servicio.empleados)} empleados.\n")

    # 2. Generación del reporte tabular
    imprimir_reporte_empleados(servicio)

    # 3. Balance general contable
    imprimir_balance_empresarial(servicio)

    # 4. Demostración interactiva del manejo de excepciones de negocio
    print("[*] Verificación de validaciones de reglas de negocio...")
    try:
        # Intento de registrar horas negativas
        EmpleadoPorHoras("ERR-01", "Empleado Inválido", 1, horas_trabajadas=-10, tarifa_hora=20_000)
    except BusinessRuleException as err:
        print(f" [PASS] Validación exitosa (Horas negativas capturadas): {err}")

    try:
        # Intento de ventas negativas
        EmpleadoPorComision("ERR-02", "Empleado Inválido", 1, salario_base=1_000_000, porcentaje_comision=0.05, total_ventas=-500)
    except BusinessRuleException as err:
        print(f" [PASS] Validación exitosa (Ventas negativas capturadas): {err}")

    # 5. Exportación del reporte a CSV para contabilidad
    archivo_csv = "reporte_nomina.csv"
    servicio.exportar_reporte(archivo_csv)
    print(f"\n[+] Reporte de nómina exportado exitosamente a '{archivo_csv}'")


if __name__ == "__main__":
    main()