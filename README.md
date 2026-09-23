# Sistema de Nómina CIPA 404 NOT FOUND

**Actividad de Aprendizaje - Unidad 3 Desarrollo y Pruebas de Software **  
**Asignatura:Ingeniería de Software
**Programa:** Ingeniería de Software  
**Institución:** Universidad de Cartagena  
**Docente:** Ureliano Peñata Hernández  

---

## Integrantes - CIPA *404 Not Found*

| Integrante | Correo Institucional | Rol Principal en el Proyecto |
| :--- | :--- | :--- |
| **Jorge Enrique Meza Rocha** (`jemezar`) | `jmezar@unicartagena.edu.co` | Integración, CLI/Reporte, Documentación y Arquitectura |
| **Juan Guillermo Hernández Gastelbondo** (`juanguillo125`) | `jhernandezg5@unicartagena.edu.co` | Orquestador Contable, Servicios y Suite de Pruebas Unitarias |
| **Ever Antonio Assia Ibañez** (`AntonioAssia`) | `eassiai@unicartagena.edu.co` | Dominio OOP, Deducciones de Ley y Reglas de Negocio |
| **Yaismer Luis Figueroa Morelo** (`Yaismer281122`) | `yfigueroam@unicartagena.edu.co` | Módulo de Exportación Contable (CSV), Persistencia y DIP |

---

## Descripción del Proyecto y Reglas de Negocio

El proyecto consiste en el diseño e implementación de un **Sistema de Nómina Empresarial** modular y robusto bajo el paradigma de **Programación Orientada a Objetos (POO)** y los principios **SOLID**, permitiendo liquidar periódicamente salarios, beneficios corporativos y deducciones para distintos esquemas laborales:

### 1. Tipos de Empleados y Devengos
* **Empleado Asalariado:**
  * Salario fijo mensual garantizado.
  * **Beneficio de Antigüedad:** Bono mensual adicional del 10% del salario fijo si cuenta con más de 5 años en la empresa.
* **Empleado por Horas:**
  * Liquidación por horas laboradas a tarifa base convenida.
  * **Horas Extras:** Jornadas superiores a 40 horas se remuneran con un recargo del **50%** ($1.5 \times$ tarifa normal).
  * No percibe bonos salariales.
* **Empleado por Comisión:**
  * Salario base garantizado más porcentaje de comisión pactado sobre el total de ventas.
  * **Bono de Desempeño Comercial:** Si las ventas del periodo superan los **$20.000.000**, recibe un bono adicional del **3%** sobre el total de ventas.
* **Empleado Temporal:**
  * Salario fijo mensual bajo contrato por tiempo definido.
  * No aplican bonos ni beneficios adicionales.

### 2. Deducciones Obligatorias de Ley
* **Seguro Social y Pensión:** Retención del 4% en Salud y 4% en Pensión (Total 8%) sobre el salario bruto.
* **ARL (Riesgos Laborales):** Tarifa base de ley para Clase I de riesgo (0.522%) o configurable.

### 3. Beneficios Adicionales
* **Empleados Permanentes (Asalariado y Comisión):** Auxilio / Bono de alimentación de **$1.000.000/mes**, cubierto directamente por la empresa.
* **Empleados por Horas:** Si su antigüedad supera 1 año, tienen la facultad opcional de ingresar al **Fondo de Ahorro**, con una deducción voluntaria del **2%** de su salario bruto.

### 4. Validaciones de Integridad y Reglas Contables
* Ningún trabajador puede registrar un salario neto negativo.
* Las horas laboradas no pueden ser inferiores a cero.
* Las ventas de un empleado comisionista no pueden ser menores a $0.
* Identificación, nombres y salarios base deben ser estrictamente válidos.

---

## 🏛️ Aplicación de Principios SOLID

El diseño de la solución garantiza mantenibilidad y extensibilidad:

1. **S - Responsabilidad Única (*Single Responsibility Principle*):**
   * Cada clase de empleado (`EmpleadoAsalariado`, `EmpleadoPorHoras`, etc.) encapsula únicamente las reglas matemáticas de su modalidad laboral.
   * `ServicioLiquidacionNomina` se responsabiliza exclusivamente de la liquidación masiva y balance de la empresa.
   * `ExportadorNominaCSV` asume la responsabilidad exclusiva de serialización y persistencia de reportes contables.

2. **O - Abierto/Cerrado (*Open/Closed Principle*):**
   * La clase abstracta `Empleado` permite añadir nuevas modalidades contractuales sin modificar el código base preexistente.
   * La interfaz abstracta `ExportadorReporte` permite incorporar nuevos formatos de exportación (JSON, Excel, PDF) sin alterar el orquestador de nómina.

3. **L - Sustitución de Liskov (*Liskov Substitution Principle*):**
   * Cualquier subtipo de `Empleado` sustituye de manera uniforme a la clase base sin alterar los contratos pre/post-condición (`calcular_salario_neto()`).

4. **I - Segregación de Interfaces (*Interface Segregation Principle*):**
   * Separación explícita de métodos de ingresos directos, beneficios corporativos y deducciones voluntarias, impidiendo dependencias innecesarias en tipos que no los aplican.

5. **D - Inversión de Dependencias (*Dependency Inversion Principle*):**
   * `ServicioLiquidacionNomina` depende de abstracciones (`Empleado` y `ExportadorReporte`), permitiendo inyección de dependencias flexible desacoplada de implementaciones concretas.

---

## Metodología de Desarrollo y Control de Versiones

El equipo implementó una combinación de **Scrum** y **Extreme Programming (XP)**:

* **Gestión de Historias de Usuario e Iteraciones (Scrum):**
  * La actividad se descompuso en historias de usuario correspondientes a perfiles contractuales, motor de deducciones, módulo de reportes/persistencia y presentación.
* **Prácticas XP Adoptadas:**
  * **Test-Driven Development (TDD) / Pruebas Continuas:** Desarrollo de suite automatizada con `unittest` cubriendo casos nominales, casos borde y persistencia de datos.
  * **Refactorización y Código Limpio:** Eliminación de números mágicos mediante constantes semánticas (`LIMITE_HORAS_ORDINARIAS`, `UMBRAL_VENTAS_BONO`), tipado estático (*Type Hints*) y comentarios técnicos según PEP-8.
  * **Revisión de Código y Colaboración en Equipo:** Distribución de commits y trazabilidad entre los 4 integrantes del CIPA en GitHub.

---

## Estructura del Repositorio

```text
actividad-u3-is/
├── src/
│   ├── __init__.py
│   ├── modelos.py          # Jerarquía OOP de Empleados, constantes y validaciones
│   ├── servicios.py        # Orquestador contable, balances y exportación
│   └── exportadores.py     # Estrategia de exportación de nómina (CSV/persistencia)
├── tests/
│   ├── __init__.py
│   └── test_nomina.py      # 19 pruebas unitarias automatizadas con unittest
├── image/
│   └── portada.png         # Recursos visuales del proyecto
├── main.py                 # Punto de entrada, reporte en consola y exportación CSV
├── reporte_nomina.csv      # Archivo consolidado de nómina generado
├── requirements.txt        # Dependencias opcionales
├── .gitignore              # Exclusiones de Git
└── README.md               # Documentación general de la actividad
```

---

## Ejecución de Pruebas Unitarias

Para ejecutar la suite automatizada de pruebas:

```bash
python tests/test_nomina.py
```
O con el módulo de descubrimiento estándar:
```bash
python -m unittest discover tests
```

Salida esperada:
```text
...................
----------------------------------------------------------------------
Ran 19 tests in 0.003s

OK
```

---

## Ejecución del Sistema

Para ejecutar la demostración completa del sistema de nómina y generar el reporte exportado:

```bash
python main.py
```
