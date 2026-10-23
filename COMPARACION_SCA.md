# Comparación de resultados reales

Fecha local: 22 de octubre de 2026 (Guatemala). Los resultados son una fotografía de las fuentes disponibles durante el laboratorio, no una prueba de explotabilidad de cada aviso.

| Medida inicial | Dependency-Check 13.0.0 | Dependency-Track 4.14.5 | DefectDojo 3.4.202 |
| --- | ---: | ---: | ---: |
| Componentes inventariados/analizados | 19 | 18 | Importa el XML |
| Componentes afectados | 9 | 8 | Importa 31 hallazgos |
| Pares componente/aviso | 31 | 28 | 31 |
| Críticos | 4 | 4 | 4 |
| Altos | 4 | 12 | 7 |
| Medios | 19 | 10 | 16 |
| Bajos | 4 | 2 | 4 |

Dependency-Check examinó 18 artefactos Maven y `src/main/webapp/jquery.min.js` (1.6.4). El SBOM Maven contiene 18 componentes; por eso Dependency-Track no recibió jQuery. Los 31 pares de Dependency-Check corresponden a 28 identificadores distintos: 27 CVE y `jquery issue:162`. Un CVE que afecta a dos módulos cuenta dos veces como par componente/aviso.

Dependency-Track sincronizó OSV para Maven (7198 avisos) y relacionó PURL con avisos GITHUB/GHSA. Se normalizaron los alias CVE para comparar con NVD: por ejemplo, `GHSA-jfh8-c2jp-5v3q` es alias de `CVE-2021-44228`. Resultado: **18 pares en común, 13 solo en Dependency-Check y 10 solo en Dependency-Track**.

| Componente y versión | Dependency-Check | Dependency-Track |
| --- | ---: | ---: |
| commons-collections 3.1 | 1 | 2 |
| commons-fileupload 1.3.3 | 2 | 2 |
| commons-io 2.6 | 2 | 2 |
| dom4j 1.6.1 | 1 | 2 |
| hibernate-core 4.0.1.Final | 2 | 2 |
| jquery 1.6.4 (archivo local) | 6 | 0 |
| log4j-api 2.12.1 | 3 | 0 |
| log4j-core 2.12.1 | 9 | 8 |
| mysql-connector-java 5.1.26 | 5 | 8 |
| org.json:json 20090211 | 0 | 2 |

Ejemplos de diferencias: Dependency-Track incorporó `CVE-2022-45688` y `CVE-2023-5072` para org.json, y `CVE-2018-1000632` para dom4j. Dependency-Check incluyó los seis avisos del archivo jQuery y tres del módulo log4j-api. MySQL tiene avisos exclusivos en ambas fuentes. Estas discrepancias requieren revisar cobertura, fechas, identificadores y rangos afectados; no implican automáticamente falsos positivos.

DefectDojo recibió el XML mediante **Dependency Check Scan**, producto JavaVulnerableLab, engagement Analisis SCA inicial, test 1. Conservó los 31 hallazgos. Clasificó como altos tres pares que Dependency-Check clasificaba como medios: `CVE-2026-34479` en log4j-api y log4j-core, y `CVE-2026-34480` en log4j-core. El importador conserva CVSS 3 (7.5) en esas entradas, mientras el reporte nativo dispone de CVSS 4. No son tres vulnerabilidades nuevas; es una diferencia de clasificación.

Los originales HTML/XML/JSON/SARIF/CSV, el SBOM, las capturas y la tabla completa se incluyen en la entrega académica. DefectDojo centraliza los hallazgos importados; no se ejecutó un tercer motor SCA al importar el XML.

Fuentes: [Dependency-Check](https://dependency-check.github.io/DependencyCheck/), [Dependency-Track](https://docs.dependencytrack.org/), [DefectDojo](https://docs.defectdojo.com/).
