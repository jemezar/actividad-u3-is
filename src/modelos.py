"""
Módulo de dominio: Modelos de Empleados y Reglas de Negocio del Sistema de Nómina.

Este módulo define la jerarquía de empleados y aplica los principios SOLID:
- S (Single Responsibility): Cada clase modela exclusivamente el cálculo de compensación y deducción de un perfil laboral.
- O (Open/Closed): La clase abstracta Empleado está abierta a la extensión para nuevos tipos de contratación sin modificar el código base.
- L (Liskov Substitution): Cualquier subclase de Empleado puede ser procesada uniformemente sin romper la invariante contable.
- I (Interface Segregation): Métodos específicos para beneficios de empresa y deducciones voluntarias desacoplados.
- D (Dependency Inversion): Los servicios de nómina dependen de la abstracción Empleado.
"""

from abc import ABC, abstractmethod


class BusinessRuleException(ValueError):
    """Excepción lanzada cuando una operación viola una regla de negocio o validación contable."""
    pass


class Empleado(ABC):
    """
    Clase abstracta base para representar a un empleado en el sistema.
    
    Establece las constantes de deducción de ley y el contrato para el cálculo
    de devengos, beneficios corporativos y deducciones.
    """

    # Deducciones obligatorias de ley según legislación y requerimientos
    PORCENTAJE_SALUD: float = 0.04    # 4% del salario bruto
    PORCENTAJE_PENSION: float = 0.04  # 4% del salario bruto
    PORCENTAJE_ARL_BASE: float = 0.00522  # 0.522% Riesgo laboral Clase I

    def __init__(self, identificacion: str, nombre: str, anios_antiguedad: int, porcentaje_arl: float = PORCENTAJE_ARL_BASE):
        """
        Inicializa un empleado base.
        
        :param identificacion: Cédula o identificador único del trabajador.
        :param nombre: Nombre completo del trabajador.
        :param anios_antiguedad: Años de permanencia en la empresa.
        :param porcentaje_arl: Porcentaje de deducción por ARL según clase de riesgo (por defecto Clase I).
        """
        if not identificacion or not identificacion.strip():
            raise BusinessRuleException("La identificación no puede estar vacía.")
        if not nombre or not nombre.strip():
            raise BusinessRuleException("El nombre no puede estar vacío.")
        if anios_antiguedad < 0:
            raise BusinessRuleException("La antigüedad no puede ser un valor negativo.")
        if porcentaje_arl < 0:
            raise BusinessRuleException("El porcentaje de ARL no puede ser negativo.")

        self.identificacion: str = identificacion.strip()
        self.nombre: str = nombre.strip()
        self.anios_antiguedad: int = anios_antiguedad
        self.porcentaje_arl: float = porcentaje_arl

    @abstractmethod
    def calcular_salario_bruto(self) -> float:
        """Calcula el total devengado por el empleado antes de aplicar deducciones o beneficios."""
        pass

    def calcular_deducciones_obligatorias(self) -> float:
        """
        Calcula las deducciones obligatorias de ley (Seguro Social, Pensión y ARL)
        aplicadas sobre el salario bruto devengado.
        """
        bruto = self.calcular_salario_bruto()
        salud = bruto * self.PORCENTAJE_SALUD
        pension = bruto * self.PORCENTAJE_PENSION
        arl = bruto * self.porcentaje_arl
        return salud + pension + arl

    def calcular_beneficios_empresa(self) -> float:
        """
        Calcula beneficios monetarios cubiertos directamente por la empresa.
        Por defecto los contratos no permanentes retornan 0.0.
        """
        return 0.0

    def calcular_deducciones_voluntarias(self) -> float:
        """
        Calcula deducciones voluntarias autorizadas por el trabajador (ej. fondo de ahorro).
        Por defecto retorna 0.0.
        """
        return 0.0

    def calcular_salario_neto(self) -> float:
        """
        Calcula el salario neto final a pagar:
        Neto = Salario Bruto + Beneficios Empresa - (Deducciones Obligatorias + Deducciones Voluntarias)
        
        Validación: Ningún empleado puede tener un salario neto negativo.
        """
        ingresos = self.calcular_salario_bruto() + self.calcular_beneficios_empresa()
        egresos = self.calcular_deducciones_obligatorias() + self.calcular_deducciones_voluntarias()
        neto = ingresos - egresos

        if neto < 0:
            raise BusinessRuleException(
                f"Inconsistencia financiera: El salario neto de {self.nombre} no puede ser negativo ({neto:.2f})."
            )
        return neto


class EmpleadoAsalariado(Empleado):
    """
    Empleado permanente con contrato laboral y salario fijo mensual.
    
    Reglas de negocio:
    - Salario fijo mensual garantizado.
    - Beneficio antigüedad: Bono mensual del 10% del salario si lleva más de 5 años en la empresa.
    - Beneficio permanente: Bono de alimentación de $1.000.000/mes cubierto por la empresa.
    """

    VALOR_BONO_ALIMENTACION: float = 1_000_000.0

    def __init__(self, identificacion: str, nombre: str, anios_antiguedad: int,
                 salario_fijo: float, porcentaje_arl: float = Empleado.PORCENTAJE_ARL_BASE):
        super().__init__(identificacion, nombre, anios_antiguedad, porcentaje_arl)
        if salario_fijo <= 0:
            raise BusinessRuleException("El salario fijo mensual debe ser mayor a cero.")
        self.salario_fijo: float = salario_fijo

    def calcular_bono_antiguedad(self) -> float:
        """Retorna el 10% del salario fijo si la antigüedad es mayor a 5 años; de lo contrario 0.0."""
        return (self.salario_fijo * 0.10) if self.anios_antiguedad > 5 else 0.0

    def calcular_salario_bruto(self) -> float:
        return self.salario_fijo + self.calcular_bono_antiguedad()

    def calcular_beneficios_empresa(self) -> float:
        # Beneficio adicional para empleado permanente
        return self.VALOR_BONO_ALIMENTACION


class EmpleadoPorHoras(Empleado):
    """
    Empleado contratado y liquidado por horas trabajadas.
    
    Reglas de negocio:
    - Pago por horas trabajadas según tarifa base acordada.
    - Horas extras (más de 40 horas semanales/periodo) se pagan con un recargo de 1.5 x la tarifa normal.
    - No recibe bonos salariales.
    - Fondo de ahorro: con más de 1 año de antigüedad tiene acceso a fondo de ahorro (2% del salario depositado),
      siempre que el empleado acepte expresamente el descuento.
    """

    LIMITE_HORAS_ORDINARIAS: float = 40.0
    FACTOR_HORA_EXTRA: float = 1.5
    PORCENTAJE_FONDO_AHORRO: float = 0.02

    def __init__(self, identificacion: str, nombre: str, anios_antiguedad: int,
                 horas_trabajadas: float, tarifa_hora: float,
                 acepta_fondo_ahorro: bool = False,
                 porcentaje_arl: float = Empleado.PORCENTAJE_ARL_BASE):
        super().__init__(identificacion, nombre, anios_antiguedad, porcentaje_arl)
        if horas_trabajadas < 0:
            raise BusinessRuleException("Las horas trabajadas no pueden ser negativas.")
        if tarifa_hora <= 0:
            raise BusinessRuleException("La tarifa por hora debe ser mayor a cero.")

        self.horas_trabajadas: float = horas_trabajadas
        self.tarifa_hora: float = tarifa_hora
        self.acepta_fondo_ahorro: bool = acepta_fondo_ahorro

    def calcular_salario_bruto(self) -> float:
        if self.horas_trabajadas <= self.LIMITE_HORAS_ORDINARIAS:
            return self.horas_trabajadas * self.tarifa_hora

        horas_regulares = self.LIMITE_HORAS_ORDINARIAS
        horas_extras = self.horas_trabajadas - self.LIMITE_HORAS_ORDINARIAS
        pago_ordinario = horas_regulares * self.tarifa_hora
        pago_extra = horas_extras * (self.tarifa_hora * self.FACTOR_HORA_EXTRA)
        return pago_ordinario + pago_extra

    def calcular_deducciones_voluntarias(self) -> float:
        # Acceso al 2% para fondo de ahorro únicamente si lleva más de 1 año y aceptó
        if self.anios_antiguedad > 1 and self.acepta_fondo_ahorro:
            return self.calcular_salario_bruto() * self.PORCENTAJE_FONDO_AHORRO
        return 0.0


class EmpleadoPorComision(Empleado):
    """
    Empleado comercial con salario base y comisiones sobre el volumen de ventas.
    
    Reglas de negocio:
    - Salario base pactado más porcentaje convenido sobre las ventas logradas.
    - Bono adicional de desempeño: Si las ventas superan los $20.000.000, recibe un 3% adicional sobre el total de ventas.
    - Beneficio permanente: Bono de alimentación de $1.000.000/mes cubierto por la empresa.
    """

    UMBRAL_VENTAS_BONO: float = 20_000_000.0
    PORCENTAJE_BONO_SUPERACION: float = 0.03
    VALOR_BONO_ALIMENTACION: float = 1_000_000.0

    def __init__(self, identificacion: str, nombre: str, anios_antiguedad: int,
                 salario_base: float, porcentaje_comision: float, total_ventas: float,
                 porcentaje_arl: float = Empleado.PORCENTAJE_ARL_BASE):
        super().__init__(identificacion, nombre, anios_antiguedad, porcentaje_arl)
        if salario_base < 0:
            raise BusinessRuleException("El salario base no puede ser negativo.")
        if porcentaje_comision < 0 or porcentaje_comision > 1:
            raise BusinessRuleException("El porcentaje de comisión debe estar en el rango [0.0, 1.0].")
        if total_ventas < 0:
            raise BusinessRuleException("Las ventas de un empleado por comisión no pueden ser menores a $0.")

        self.salario_base: float = salario_base
        self.porcentaje_comision: float = porcentaje_comision
        self.total_ventas: float = total_ventas

    def calcular_salario_bruto(self) -> float:
        comision_ventas = self.total_ventas * self.porcentaje_comision
        bono_superacion = (
            (self.total_ventas * self.PORCENTAJE_BONO_SUPERACION)
            if self.total_ventas > self.UMBRAL_VENTAS_BONO
            else 0.0
        )
        return self.salario_base + comision_ventas + bono_superacion

    def calcular_beneficios_empresa(self) -> float:
        # Beneficio adicional para empleado permanente
        return self.VALOR_BONO_ALIMENTACION


class EmpleadoTemporal(Empleado):
    """
    Empleado vinculado mediante contrato a término definido con salario fijo pactado.
    
    Reglas de negocio:
    - Salario fijo mensual pactado.
    - No aplican bonos ni beneficios adicionales (alimentación ni fondos de ahorro).
    """

    def __init__(self, identificacion: str, nombre: str, anios_antiguedad: int,
                 salario_mensual: float, porcentaje_arl: float = Empleado.PORCENTAJE_ARL_BASE):
        super().__init__(identificacion, nombre, anios_antiguedad, porcentaje_arl)
        if salario_mensual <= 0:
            raise BusinessRuleException("El salario mensual debe ser un valor positivo.")
        self.salario_mensual: float = salario_mensual

    def calcular_salario_bruto(self) -> float:
        return self.salario_mensual