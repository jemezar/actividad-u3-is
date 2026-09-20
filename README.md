# Sistema de Nómina Orientado a Objetos - CIPA

Proyecto académico desarrollado para la Universidad de Cartagena con arquitectura limpia, principios SOLID y metodología ágil Scrum con TDD.

## Metodología de Desarrollo
* **Marco de trabajo:** Scrum apoyado con prácticas de Extreme Programming (XP).
* **Control de versiones:** Git con convención semántica de commits y ramas organizadas por historias de usuario.
* **Pruebas Continuas:** Suite automatizada con `unittest` que asegura las reglas de nómina.

## Principios SOLID Implementados
* **S (Responsabilidad Única):** Clases separadas para modelar entidades (`src/modelos.py`) y para orquestar la liquidación contable (`src/servicios.py`).
* **O (Abierto/Cerrado):** La clase base `Empleado` permite integrar nuevos esquemas de contratación sin modificar el código preexistente.
* **L (Sustitución de Liskov):** Todo subtipo de `Empleado` responde de forma consistente a `calcular_salario_neto()` y `calcular_salario_bruto()`.
* **I (Segregación de Interfaces):** Beneficios y deducciones opcionales desacoplados por comportamiento.
* **D (Inversión de Dependencias):** Los servicios de nómina dependen de la abstracción `Empleado`, no de implementaciones concretas.

## Ejecución de Pruebas Unitarias
Ejecuta en la raíz del proyecto:
```bash