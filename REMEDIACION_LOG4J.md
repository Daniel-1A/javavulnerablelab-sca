# Remediación de Log4Shell

El POM original incorpora log4j-api y log4j-core 2.12.1. El análisis inicial detectó `CVE-2021-44228` (Log4Shell) en log4j-core. La rama `codex/remediar-log4j` actualiza ambos módulos a **2.25.5**, manteniendo sus versiones alineadas y la compatibilidad con Java 8 o posterior.

| Verificación local | Antes | Después |
| --- | --- | --- |
| Versión de ambos módulos | 2.12.1 | 2.25.5 |
| Pares componente/aviso | 31 | 19 |
| Componentes afectados | 9 | 7 |
| Críticos / altos / medios / bajos | 4 / 4 / 19 / 4 | 2 / 4 / 11 / 2 |
| CVE-2021-44228 | Presente | Ausente |
| Componentes en SBOM | 18 | 18 |

Se retiraron los 12 pares asociados con ambos módulos Log4j y no aparecieron pares nuevos en el escaneo posterior. El resto de dependencias vulnerables permanece para mostrar el alcance concreto de esta corrección. **La aplicación no queda libre de vulnerabilidades.**

## Comprobaciones realizadas

1. Escaneo inicial y posterior con Dependency-Check 13.0.0 y Java 17, conservando reportes originales completos. La comprobación automatizada de ausencia de Log4Shell falla con el reporte inicial y pasa con el posterior.
2. SBOM posterior CycloneDX 1.6: 18 componentes; únicamente cambian las versiones de los dos módulos Log4j.
3. Compilación desde cero de las 19 fuentes Java en una copia sin `target`, con Maven, JDK 8 y `maven-compiler-plugin:3.14.0:compile`: exit 0. Se usa JDK 8 porque es el entorno de compilación de la aplicación original; con Java 17 falta `javax.xml.bind` en `JwtUtil.java`, un problema previo a esta actualización. Las herramientas de análisis y el pipeline sí utilizan Java 17, como solicita la tarea.

No se ejecutó una prueba funcional completa ni se desplegó la aplicación vulnerable. La compilación y el nuevo escaneo prueban resolución, compilación y desaparición de los avisos en el inventario analizado; no sustituyen pruebas funcionales.

## Cómo revisar la propuesta

La referencia inicial permanece en `main` y la actualización se presenta en un PR. Las alertas del PR corresponden a su revisión analizada. Hasta fusionar el PR, las alertas de `main` siguen reflejando el POM original; no deben confundirse con el resultado corregido de la propuesta.

Fuentes oficiales: [notas de Log4j 2.25.5](https://logging.apache.org/log4j/2.x/release-notes.html), [seguridad de Apache Logging](https://logging.apache.org/security.html).
