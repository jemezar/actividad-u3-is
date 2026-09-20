"""Módulo con las entidades de dominio y tipos de empleados."""
from abc import ABC, abstractmethod


class BusinessRuleException(ValueError):
    """Excepción para violaciones de reglas de negocio."""
    pass


class Empleado(ABC):
    """Clase abstracta base para la jerarquía de empleados."""

    PORCENTAJE_SALUD = 0.04
    PORCENTAJE_PENSION = 0.04
    PORCENTAJE_ARL = 0.00522  # Tarifa base de ley ARL Clase I (0.522%)

    def __init__(self, identificacion: str, nombre: str, anios_antiguedad: int):
        if anios_antiguedad < 0:
            raise BusinessRuleException("La antigüedad no puede ser negativa.")
        self.identificacion = identificacion
        self.nombre = nombre
        self.anios_antiguedad = anios_antiguedad

    @abstractmethod
    def calcular_salario_bruto(self) -> float:
        """Calcula el total devengado base antes de deducciones."""
        pass

    def calcular_deducciones_obligatorias(self) -> float:
        """Aportes legales obligatorios: Salud, Pensión y ARL."""
        bruto = self.calcular_salario_bruto()
        salud = bruto * self.PORCENTAJE_SALUD
        pension = bruto * self.PORCENTAJE_PENSION
        arl = bruto * self.PORCENTAJE_ARL
        return salud + pension + arl

    def calcular_beneficios_empresa(self) -> float:
        """Beneficios monetarios directos otorgados por la empresa."""
        return 0.0

    def calcular_deducciones_voluntarias(self) -> float:
        """Deducciones opcionales autorizadas por el trabajador."""
        return 0.0

    def calcular_salario_neto(self) -> float:
        """Calcula el total a pagar al trabajador verificando saldos positivos."""
        total_ingresos = self.calcular_salario_bruto() + self.calcular_beneficios_empresa()
        total_descuentos = self.calcular_deducciones_obligatorias() + self.calcular_deducciones_voluntarias()
        neto = total_ingresos - total_descuentos
        if neto < 0:
            raise BusinessRuleException(f"Error: Salario neto negativo para {self.nombre}.")
        return neto


class EmpleadoAsalariado(Empleado):
    """Empleado permanente con salario mensual y bono por antigüedad."""

    def __init__(self, identificacion: str, nombre: str, anios_antiguedad: int, salario_fijo: float):
        super().__init__(identificacion, nombre, anios_antiguedad)
        if salario_fijo <= 0:
            raise BusinessRuleException("El salario fijo debe ser mayor a cero.")
        self.salario_fijo = salario_fijo

    def calcular_salario_bruto(self) -> float:
        bono = (self.salario_fijo * 0.10) if self.anios_antiguedad > 5 else 0.0
        return self.salario_fijo + bono

    def calcular_beneficios_empresa(self) -> float:
        return 1_000_000.0  # Bono de alimentación


class EmpleadoPorHoras(Empleado):
    """Empleado liquidado por tarifa horaria y recargos."""

    def __init__(self, identificacion: str, nombre: str, anios_antiguedad: int,
                 horas_trabajadas: float, tarifa_hora: float, acepta_fondo_ahorro: bool = False):
        super().__init__(identificacion, nombre, anios_antiguedad)
        if horas_trabajadas < 0:
            raise BusinessRuleException("Las horas trabajadas no pueden ser negativas.")
        if tarifa_hora <= 0:
            raise BusinessRuleException("La tarifa por hora debe ser mayor a cero.")

        self.horas_trabajadas = horas_trabajadas
        self.tarifa_hora = tarifa_hora
        self.acepta_fondo_ahorro = acepta_fondo_ahorro

    def calcular_salario_bruto(self) -> float:
        if self.horas_trabajadas <= 40:
            return self.horas_trabajadas * self.tarifa_hora
        horas_regulares = 40
        horas_extras = self.horas_trabajadas - 40
        return (horas_regulares * self.tarifa_hora) + (horas_extras * self.tarifa_hora * 1.5)

    def calcular_deducciones_voluntarias(self) -> float:
        if self.anios_antiguedad > 1 and self.acepta_fondo_ahorro:
            return self.calcular_salario_bruto() * 0.02
        return 0.0


class EmpleadoPorComision(Empleado):
    """Empleado con base salarial más incentivos por ventas."""

    def __init__(self, identificacion: str, nombre: str, anios_antiguedad: int,
                 salario_base: float, porcentaje_comision: float, total_ventas: float):
        super().__init__(identificacion, nombre, anios_antiguedad)
        if salario_base < 0:
            raise BusinessRuleException("El salario base no puede ser negativo.")
        if total_ventas < 0:
            raise BusinessRuleException("Las ventas no pueden ser menores a $0.")

        self.salario_base = salario_base
        self.porcentaje_comision = porcentaje_comision
        self.total_ventas = total_ventas

    def calcular_salario_bruto(self) -> float:
        comision_base = self.total_ventas * self.porcentaje_comision
        bono_meta = (self.total_ventas * 0.03) if self.total_ventas > 20_000_000 else 0.0
        return self.salario_base + comision_base + bono_meta

    def calcular_beneficios_empresa(self) -> float:
        return 1_000_000.0  # Bono de alimentación


class EmpleadoTemporal(Empleado):
    """Empleado por contrato a término fijo, sin beneficios extralegales."""

    def __init__(self, identificacion: str, nombre: str, anios_antiguedad: int, salario_mensual: float):
        super().__init__(identificacion, nombre, anios_antiguedad)
        if salario_mensual <= 0:
            raise BusinessRuleException("El salario mensual debe ser positivo.")
        self.salario_mensual = salario_mensual

    def calcular_salario_bruto(self) -> float:
        return self.salario_mensual