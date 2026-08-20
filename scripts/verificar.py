#!/usr/bin/env python3
"""
Verifica las paginas del sitio. Cero dependencias: solo la libreria estandar.

Chequea, para cada .html del repo:
  1. Que el HTML este bien formado (etiquetas que abren y cierran donde corresponde).
  2. Que tenga <title> y un <h1>.
  3. Que los links y las imagenes que apuntan a archivos locales existan de verdad.

No chequea links externos a proposito: dependen de que un servidor de otro este
vivo, y un CI que falla por eso deja de ser una senal util y pasa a ser ruido.
"""

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

RAIZ = Path(__file__).resolve().parent.parent

# Etiquetas que no cierran nunca; no cuentan para el balance.
VACIAS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


class Revisor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pila = []
        self.errores = []
        self.refs = []
        self.tiene_title = False
        self.tiene_h1 = False

    def handle_starttag(self, tag, attrs):
        if tag not in VACIAS:
            self.pila.append((tag, self.getpos()[0]))
        if tag == "title":
            self.tiene_title = True
        if tag == "h1":
            self.tiene_h1 = True
        for nombre, valor in attrs:
            if nombre in ("href", "src") and valor:
                self.refs.append((valor, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VACIAS:
            return
        if not self.pila:
            self.errores.append(f"linea {self.getpos()[0]}: </{tag}> sin apertura")
            return
        abierta, linea = self.pila.pop()
        if abierta != tag:
            self.errores.append(
                f"linea {self.getpos()[0]}: se cierra </{tag}> pero estaba abierta "
                f"<{abierta}> (linea {linea})"
            )


def revisar(archivo):
    fallos = []
    r = Revisor()
    r.feed(archivo.read_text(encoding="utf-8"))

    fallos += r.errores
    fallos += [f"etiqueta <{t}> (linea {l}) nunca se cierra" for t, l in r.pila]

    if not r.tiene_title:
        fallos.append("falta <title>: es lo que se ve en la pestana del navegador")
    if not r.tiene_h1:
        fallos.append("falta un <h1>: la pagina no tiene titulo visible")

    for ref, linea in r.refs:
        partes = urlparse(ref)
        if partes.scheme or partes.netloc or ref.startswith(("#", "mailto:", "tel:", "data:")):
            continue  # externo o ancla: no se chequea
        destino = (archivo.parent / unquote(partes.path)).resolve()
        if not destino.exists():
            fallos.append(f"linea {linea}: apunta a '{ref}', que no existe en el repo")

    return fallos


def main():
    paginas = sorted(p for p in RAIZ.rglob("*.html") if ".git" not in p.parts)

    if not paginas:
        print("No hay ninguna pagina .html en el repo.")
        return 1

    total = 0
    for pagina in paginas:
        rel = pagina.relative_to(RAIZ)
        fallos = revisar(pagina)
        if fallos:
            total += len(fallos)
            print(f"\n✗ {rel}")
            for f in fallos:
                print(f"    {f}")
        else:
            print(f"✓ {rel}")

    if total:
        print(f"\n{total} problema(s) en {len(paginas)} pagina(s).")
        return 1

    print(f"\nTodo bien: {len(paginas)} pagina(s) sin problemas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
