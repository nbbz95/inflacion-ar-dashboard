"""Descarga la serie, calcula indicadores y arma el sitio estático en site/."""

import argparse
import json
import shutil
import urllib.request
from pathlib import Path

from pipeline.procesar import armar_salida

FUENTE = "https://api.argentinadatos.com/v1/finanzas/indices/inflacion"


def descargar(url=FUENTE):
    req = urllib.request.Request(url, headers={"User-Agent": "inflacion-ar-dashboard"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destino", default="site", type=Path)
    parser.add_argument("--desde-archivo", type=Path, help="Usar un JSON local en lugar de la API")
    args = parser.parse_args()

    registros = json.loads(args.desde_archivo.read_text()) if args.desde_archivo else descargar()
    salida = armar_salida(registros)
    shutil.copytree(Path(__file__).parent.parent / "web", args.destino, dirs_exist_ok=True)
    (args.destino / "datos.json").write_text(json.dumps(salida, ensure_ascii=False), encoding="utf-8")
    print(f"Dashboard generado en {args.destino}, último mes {salida['ultimo_mes']}")


if __name__ == "__main__":
    main()
