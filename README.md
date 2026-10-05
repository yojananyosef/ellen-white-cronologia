# Ellen G. White — Vida y ministerio profético (1827–1915)

Documento de investigación sobre la vida, el ministerio profético y la obra de
Ellen Gould Harmon White, cofundadora de la Iglesia Adventista del Séptimo Día.

## Contenido

| Archivo | Qué es |
|---|---|
| `ellen-white-cronologia.html` | Documento principal, autónomo (sin dependencias JS), con línea de tiempo horizontal |
| `ellen-white-linea-de-tiempo.md` | Los mismos datos en Markdown, como fuente editable |
| `construir.py` | Script único: Markdown → `secs.json` → HTML |
| `generador.py` | Script que produce el HTML a partir del JSON parseado |
| `secs.json` | Datos ya parseados que consume el generador |

## Estructura del documento

1. **Portada** — partículas animadas, que citan la visión de los «ríos de luz»
   (Dorchester, Massachusetts, 18 de noviembre de 1848).
2. **Sismograma** — cada barra es un año entre 1827 y 1949; su altura, el número de
   eventos registrados. Los años vacíos también dicen algo: son los que ella pasó
   escribiendo.
3. **La cinta de los años** — 85 columnas, una por año con actividad. Se desplaza
   lateralmente al hacer scroll vertical. Botón circular para saltar de sección.
4. **La cronología en extenso** — 8 etapas, cada una con su tesis argumentativa.
5. **Las visiones** — 79 experiencias proféticas con fecha y lugar.
6. **Lo que publicó** — 63 títulos en vida + 16 compilaciones póstumas.
7. **Dieciséis casas** — mapa de residencias y traslados.
8. **Siete ejes para el argumento** — la tesis que sostiene cada tramo.

Las notas de cotejo del documento (qué se corrigió y con qué fuente) ya **no se
publican**: viven en `privado/`, carpeta que está en `.gitignore`. Se retiraron
porque hablan del proceso de redacción y, sin ese contexto, se leen como
afirmaciones sobre la historia de Ellen White.

## Datos de control

- 26 nov 1827, Gorham, Maine — 16 jul 1915, Elmshaven, California
- Gemela; cuatro hijos; viuda de James Springer White
- ~2.000 visiones y sueños en 70 años
- ~40 libros y ~5.000 artículos de revista durante su vida
- Nunca fue ordenada ni electa a cargo oficial alguno

## Fuentes consultadas

- [whiteestate.org](https://www.whiteestate.org) — Ellen G. White® Estate
- [egwwritings.org](https://egwwritings.org) — sus escritos
- [encyclopedia.adventist.org](https://encyclopedia.adventist.org) — Enciclopedia de los Adventistas del Séptimo Día
- [adventistarchives.org](https://www.adventistarchives.org) — Office of Archives, Statistics, and Research
- [digitalcommons.andrews.edu](https://digitalcommons.andrews.edu) — EGW Center for Study / AUSS
- *A Comprehensive List of Ellen G. White's Visions*, AskAnAdventistFriend (revisado por el EGW Estate)
- Informe Estadístico Anual (ASR) de 1915, archivado en ASTR
- Actas de la Confererencia General de 1863 a 1888 (ASTR)

## Bibliografía académica

**Básica**
- Douglass, Herbert E. *Mensajera del Señor: El ministerio profético de Elena de White*. Asociación Casa Editora Sudamericana, 2000.
- Fortin, Denis y Jerry Moon. *Enciclopedia de Elena G. de White*. Asociación Casa Editora Sudamericana, 2020.
- Knight, George R. *Introducción a los escritos de Elena G. de White*. 2014.
- Timm, Alberto R. y Dwain N. Esmond (eds.). *El don de profecía en las escrituras y la historia*. 2018.

**Complementaria**
- Land, Gary. *El mundo de Elena G. White*. 2003.
- Pfandl, Gerhard. *El don de profecía: El lugar de Elena G. de White en la iglesia remanente de Dios*. 2008.
- Schwarz, Richard W. y Floyd Greenleaf. *Portadores de luz*. 2002.
- Douglass, Herbert E. *Profecías dramáticas de Elena de White*. 2009.
- Delafield, D. A. *Elena G. de White en Europa*. 1979.
- Viera, Juan Carlos. *La voz del Espíritu*. 1998.
- White, Arthur L. *Ellen G. White*. 6 vols., Review and Herald, 1986.

## Advertencia sobre el uso

El cotejo interno se hizo y se resolvió: el supuesto incendio de Battle Creek
College no existió (el college cerró en 1882 por disputas sobre la finalidad de
las escuelas adventistas y se mudó a Berrien Springs en 1901), la controversia
editorial de 1911–1915 es un episodio real y distinto de lo que se contaba, y
la cifra de miembros de 1915 (136.879) viene del Informe Estadístico Anual de
ese año, archivado en ASTR. El detalle está en `privado/`, que no se publica.

Antes de citar, cotejar con la bibliografía académica y con los documentos del
EGW Estate y de ASTR.

## Uso técnico

El HTML no requiere servidor ni dependencias: se abre con doble clic.
Sólo enlaza Google Fonts (Spectral e Inter); sin esa conexión cae a una serif
del sistema. Incluye hoja de impresión.

Para regenerar tras editar el Markdown:

```bash
python3 construir.py
```

Ese script hace los dos pasos (parsear el Markdown a `secs.json`, luego invocar
`generador.py`) y resuelve las rutas por sí solo, así que funciona desde
cualquier directorio y en cualquier máquina. Si solo estás tocando el
generador y no quieres reparsear el Markdown:

```bash
python3 construir.py --sin-json
```

Los datos se leen de `secs.json` junto al script. Para usar un JSON alternativo
sin tocar el código, define `SECS_JSON`:

```bash
SECS_JSON=/ruta/otro.json python3 generar.py
```
