#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reconstruye el sitio completo desde el Markdown fuente:

    ellen-white-linea-de-tiempo.md
        -> secs.json            (datos parseados)
        -> ellen-white-cronologia.html  (documento autonomo)

Uso:
    python3 construir.py

No requiere dependencias externas: solo la biblioteca estandar de Python 3.
Si secs.json ya existe y se pasa --sin-json, se reutiliza (util para iterar
sobre el generador sin reparsear el Markdown).
"""
import io, json, os, re, subprocess, sys

BASE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(BASE, "ellen-white-linea-de-tiempo.md")
JSON = os.path.join(BASE, "secs.json")
GEN = os.path.join(BASE, "generador.py")


def parse_markdown(ruta_md):
    """Convierte el Markdown en la estructura que consume generador.py.

    Una seccion es todo lo que sigue a un encabezado '## '. Dentro de cada
    seccion se reconocen dos cosas: parrafos introductorios (lineas sueltas) y
    tablas de Markdown (lineas que empiezan por '|' y van seguidas de una fila
    de separadores).
    """
    src = io.open(ruta_md, encoding="utf-8").read().split("\n")
    secciones, cur, i = [], None, 0

    while i < len(src):
        ln = src[i]

        if ln.startswith("## "):
            cur = {"title": ln[3:].strip(), "rows": [], "intro": []}
            secciones.append(cur)
            i += 1
            continue

        if cur is not None:
            # cabecera de tabla + fila de separadores
            es_cabecera = (
                ln.startswith("|")
                and i + 1 < len(src)
                and set(src[i + 1].replace("|", "").strip()) <= set("-: ")
                and src[i + 1].strip()
            )
            if es_cabecera:
                head = [c.strip() for c in ln.strip().strip("|").split("|")]
                i += 2
                filas = []
                while i < len(src) and src[i].startswith("|"):
                    celdas = [c.strip() for c in src[i].strip().strip("|").split("|")]
                    # una fila puede traer menos celdas que la cabecera (p. ej. '---')
                    while len(celdas) < len(head):
                        celdas.append("")
                    filas.append(celdas[: len(head)])
                    i += 1
                cur["rows"].append({"head": head, "data": filas})
                continue

            # parrafo suelto
            if ln.strip() and not ln.startswith("---") and not ln.startswith("|"):
                cur["intro"].append(ln.strip())

        i += 1

    return secciones


def main():
    reutilizar = "--sin-json" in sys.argv

    if reutilizar and os.path.exists(JSON):
        print("usando secs.json existente (--sin-json)")
    else:
        secciones = parse_markdown(MD)
        io.open(JSON, "w", encoding="utf-8").write(
            json.dumps(secciones, ensure_ascii=False)
        )
        tablas = sum(len(s["rows"]) for s in secciones)
        filas = sum(len(t["data"]) for s in secciones for t in s["rows"])
        print(f"secs.json: {len(secciones)} secciones, {tablas} tablas, {filas} filas")

    print("generando HTML...")
    subprocess.run([sys.executable, GEN], check=True, cwd=BASE)

    html = os.path.join(BASE, "ellen-white-cronologia.html")
    print(f"listo: {html} ({os.path.getsize(html):,} bytes)")


if __name__ == "__main__":
    main()
