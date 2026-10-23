# Respuestas de análisis

## 19. ¿Qué diferencia hay entre SAST y SCA? ¿Por qué una aplicación necesita ambos?

SAST examina el código propio sin ejecutar la aplicación y busca patrones o flujos que pueden producir fallos, como una consulta SQL construida con una entrada sin validar. SCA identifica los componentes de terceros y sus versiones para relacionarlos con vulnerabilidades publicadas. En el laboratorio anterior, Bearer examinó el código de Juice Shop; en este laboratorio, Dependency-Check y Dependency-Track analizan las librerías de JavaVulnerableLab.

Se necesitan ambos porque corregir el código de la aplicación no actualiza automáticamente sus librerías, y actualizar una librería no corrige todos los errores del código propio. Por ejemplo, una aplicación puede tener consultas parametrizadas y aun así incluir una versión vulnerable de Log4j. Los hallazgos de ambas técnicas requieren revisión: identificar una dependencia vulnerable no demuestra por sí solo que un atacante pueda explotar todas sus funciones en esa aplicación.

Fuentes: [OWASP: herramientas de SAST](https://community.owasp.org/Source_Code_Analysis_Tools) y [OWASP Dependency-Check](https://owasp.org/projects/dependency-check).

## 20. ¿Qué es una dependencia transitiva y por qué es difícil de controlar? Da un ejemplo de este proyecto.

Una dependencia transitiva es una librería que otra dependencia incorpora indirectamente. En este proyecto, el árbol de Maven y el gráfico del SBOM muestran `JavaVulnerableLab -> org.hibernate:hibernate-core:4.0.1.Final -> dom4j:dom4j:1.6.1`. El POM declara Hibernate, pero no declara directamente dom4j. Dependency-Track detectó dos avisos para dom4j 1.6.1 en el análisis inicial con OSV.

Estas dependencias son difíciles de controlar porque el desarrollador puede no conocer todas las versiones resueltas dentro de una cadena. También pueden cambiar al actualizar otra librería, llegar por varias rutas o quedar condicionadas por reglas de resolución de versiones. Para gestionarlas hay que revisar el árbol completo y el SBOM, actualizar la dependencia que las introduce o fijar una versión compatible mediante dependencyManagement y comprobar que la aplicación siga funcionando.

Evidencias reproducibles: `mvn org.apache.maven.plugins:maven-dependency-plugin:3.8.1:tree` y `target/bom.json`. El SBOM inicial contiene 18 componentes: 10 dependencias directas no incluidas en el ámbito test y 8 componentes adicionales únicos.

## 21. ¿Qué ventaja tiene Dependency-Track frente a ejecutar Dependency-Check solo en el pipeline?

El pipeline analiza una revisión cuando se produce un evento. Una vulnerabilidad puede publicarse después de la última ejecución, aunque nadie cambie el código. Dependency-Track conserva el inventario recibido mediante el SBOM y lo vuelve a evaluar al actualizar sus fuentes de vulnerabilidades; por ello puede avisar de riesgos nuevos sin esperar otro commit.

Además, permite consultar qué proyectos y versiones utilizan un componente, mantener decisiones de auditoría y aplicar políticas sobre vulnerabilidades, licencias o antigüedad. El pipeline aporta una revisión asociada a cada cambio y Dependency-Track aporta seguimiento del inventario a lo largo del tiempo.

Fuente: [documentación oficial de Dependency-Track](https://docs.dependencytrack.org/).

## 22. ¿Por qué pueden reportar resultados distintos para el mismo proyecto?

Las herramientas pueden consultar fuentes y actualizaciones diferentes. Dependency-Check utiliza evidencias de los artefactos para asociarlos con CPE y consultar CVE del NVD. Dependency-Track puede relacionar los PURL del SBOM con avisos de OSV y otras fuentes habilitadas. La cobertura de cada fuente, sus intervalos de versiones y la fecha de sincronización influyen en los resultados.

También importan el ámbito de dependencias incluido, los analizadores habilitados, las exclusiones y las decisiones de auditoría. Un mismo problema puede tener identificadores distintos: en el análisis inicial de Dependency-Track, `GHSA-jfh8-c2jp-5v3q` tiene como alias `CVE-2021-44228` (Log4Shell). Comparar los números de avisos sin unificar esos alias podría aparentar una discrepancia que no existe. El informe de entrega compara los componentes y los identificadores normalizados de los reportes obtenidos.

Fuentes: [motor de Dependency-Check](https://owasp.org/projects/dependency-check) y [fuentes de Dependency-Track](https://docs.dependencytrack.org/).

## 23. Si una librería vulnerable no tiene versión corregida, ¿qué alternativas hay?

Primero hay que confirmar que la versión y la funcionalidad afectadas están presentes y evaluar la exposición concreta. Las alternativas incluyen sustituir o retirar la librería, desactivar la función vulnerable o aplicar un parche mantenido y probado. Como medidas compensatorias pueden limitarse las entradas que llegan a la función afectada, los privilegios del proceso y sus conexiones de red, además de reforzar la vigilancia.

Si la corrección inmediata no resulta viable, se debe registrar una aceptación temporal del riesgo con responsable, justificación, controles y fecha de revisión; conservar el componente en el SBOM y monitorear nuevas soluciones. Una exclusión del analizador debe justificarse con evidencia de falso positivo o no aplicabilidad; ocultar un aviso no elimina una vulnerabilidad real.

Fuente: [OWASP: gestión de dependencias vulnerables](https://cheatsheetseries.owasp.org/cheatsheets/Vulnerable_Dependency_Management_Cheat_Sheet.html).
