# Laboratorio SCA con JavaVulnerableLab

Proyecto académico basado en [CSPF-Founder/JavaVulnerableLab](https://github.com/CSPF-Founder/JavaVulnerableLab), revisión original `626a106a49777507beb51955d19ef9d271a9d4a5`. El código original conserva su licencia GPL-2.0 y se importa sin su historial Git.

## Herramientas y alcance

- JDK 17 y Maven 3.9 mediante la imagen oficial `maven:3.9-eclipse-temurin-17`.
- OWASP Dependency-Check Maven Plugin 13.0.0.
- CycloneDX Maven Plugin 2.9.3, SBOM JSON, esquema 1.6.
- Dependency-Track: proyecto `JavaVulnerableLab`, versión `1.0`.
- DefectDojo: producto `JavaVulnerableLab`, importación `Dependency Check Scan`.

El análisis inicial utiliza las dependencias vulnerables del proyecto. No es necesario ejecutar la aplicación web para realizar SCA.

## Análisis local

Guarda la clave NVD activada como variable de entorno `NVD_API_KEY`, sin incluir su valor en comandos versionados. `.mvn/settings-sca.xml` referencia esa variable y la entrega al plugin mediante un servidor Maven llamado `nvd`.

```powershell
mvn -B --no-transfer-progress -s .mvn/settings-sca.xml org.owasp:dependency-check-maven:13.0.0:check "-Dformat=ALL" "-DnvdApiServerId=nvd" "-DossIndexAnalyzerEnabled=false" "-DfailBuildOnCVSS=11"
mvn -B --no-transfer-progress org.cyclonedx:cyclonedx-maven-plugin:2.9.3:makeAggregateBom "-DoutputFormat=json" "-DschemaVersion=1.6"
mvn -B --no-transfer-progress org.apache.maven.plugins:maven-dependency-plugin:3.8.1:tree
```

Alternativa con Docker, desde la raíz del repositorio:

```powershell
docker run --rm -e NVD_API_KEY -v "${PWD}:/src" -v sca-maven-cache:/root/.m2 -w /src maven:3.9-eclipse-temurin-17 mvn -B --no-transfer-progress -s .mvn/settings-sca.xml org.owasp:dependency-check-maven:13.0.0:check "-Dformat=ALL" "-DnvdApiServerId=nvd" "-DossIndexAnalyzerEnabled=false" "-DfailBuildOnCVSS=11"
docker run --rm -v "${PWD}:/src" -v sca-maven-cache:/root/.m2 -w /src maven:3.9-eclipse-temurin-17 mvn -B --no-transfer-progress org.cyclonedx:cyclonedx-maven-plugin:2.9.3:makeAggregateBom "-DoutputFormat=json" "-DschemaVersion=1.6"
```

Dependency-Check genera `target/dependency-check-report.html`, `.xml`, `.json` y `.sarif`. CycloneDX genera `target/bom.json`. Los reportes y `target/` quedan fuera de Git.

## Pipeline

`.github/workflows/sca-dependency-check.yml` analiza los push a `main`, los PR hacia `main` y las ejecuciones manuales. Prepara Java 17, obtiene `NVD_API_KEY` desde los secretos de Actions, reutiliza la base NVD y publica SARIF con la categoría `dependency-check`. El segundo trabajo genera y publica `bom.json` como artefacto.

Cada línea del YAML tiene un comentario. El permiso `security-events: write` se limita al trabajo que publica SARIF; el trabajo SBOM solo hereda lectura del repositorio. Las publicaciones de resultados se intentan con `always()` y comprueban la existencia del SARIF antes de cargarlo.

La primera copia del NVD se prepara con `scripts/download_nvd_feeds.py`: valida la clave contra la API, descarga los feeds oficiales en rangos HTTP reanudables y comprueba el SHA-256 del JSON descomprimido y su longitud contra los metadatos oficiales. El plugin importa esos archivos mediante su opción de espejo `nvdDatafeedUrl`, servidos temporalmente solo en `127.0.0.1` del runner. La marca de preparación se crea después de una importación correcta y se conserva junto con la base NVD en la caché. Las ejecuciones siguientes reutilizan esa base y actualizan normalmente por API con páginas pequeñas. Este procedimiento evita los cortes observados en las respuestas grandes del NVD y mantiene intactos los datos de vulnerabilidades.

`failBuildOnCVSS=11` conserva el comportamiento informativo del laboratorio: CVSS tiene un máximo de 10, por lo que las vulnerabilidades se muestran en los reportes y en Code scanning sin impedir la publicación de evidencias. Los errores del analizador sí hacen fallar el trabajo. Una política de producción puede fijar 7 para bloquear por hallazgos altos o críticos; entonces podrían seguir fallando los análisis aun después de corregir solo Log4j, porque el proyecto contiene otras dependencias vulnerables.

## Dependencias transitivas

El árbol Maven inicial contiene `JavaVulnerableLab -> hibernate-core:4.0.1.Final -> dom4j:1.6.1`. `dom4j` no aparece como dependencia directa en el POM y llega al proyecto a través de Hibernate. El informe contrasta esta ruta con el gráfico de Dependency-Track y con los hallazgos reales.

## Documentación oficial

- [Configuración de Dependency-Check](https://dependency-check.github.io/DependencyCheck/dependency-check-maven/configuration.html)
- [Plugin CycloneDX](https://github.com/CycloneDX/cyclonedx-maven-plugin)
- [Dependency-Track](https://docs.dependencytrack.org/)
- [DefectDojo](https://docs.defectdojo.com/)
- [Seguridad de Apache Logging](https://logging.apache.org/security.html)

## Adaptación para publicar el laboratorio

GitHub Push Protection detectó valores con formato de clave de Stripe en dos archivos del proyecto original: `backup/config.properties.bak` e `integrations.jsp`. Se sustituyeron por `STRIPE_KEY_PLACEHOLDER_FOR_SCA_LAB` antes de publicar el historial inicial. Se mantiene el POM original para el análisis de referencia; este ajuste de ejemplos no modifica dependencias.
