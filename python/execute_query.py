"""Ejecuta una consulta escrita en sintaxis mongosh (.ts) usando pymongo.

python3 python/execute_query.py               # corre consultas/libre.ts
python3 python/execute_query.py E9            # corre consultas/E09_*.ts
python3 python/execute_query.py P --etapas    # Pizzagram, mostrando cada etapa del pipeline
python3 python/execute_query.py E3 --atlas    # contra la base del taller en Atlas
python3 python/execute_query.py E9 --pymongo  # muestra también la llamada pymongo equivalente
"""

import argparse
import sys
import time

from pymongo.errors import PyMongoError

from clase.conexion import get_db
from clase.ejercicios import (
    BaseVacia,
    EjercicioNoEncontrado,
    base_de,
    cargar,
    como_pymongo,
    ejecutar,
    resolver,
    verificar_base,
)
from clase.formato import FIN, GRIS, NEGRITA, imprimir
from clase.mongosh import ErrorDeSintaxis, codigo_visible, metadatos


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ejercicio", nargs="?", default="libre", help="E1..E14, P, errores/E03, libre o una ruta .ts")
    ap.add_argument("--atlas", action="store_true", help="usar la base del taller en Atlas (solo tweets)")
    ap.add_argument("--etapas", action="store_true", help="mostrar la salida después de cada etapa del pipeline")
    ap.add_argument("--pymongo", action="store_true", help="mostrar la llamada pymongo equivalente")
    ap.add_argument("--max", type=int, default=20, help="máximo de documentos a mostrar (20)")
    args = ap.parse_args()

    try:
        ruta = resolver(args.ejercicio)
        texto = ruta.read_text(encoding="utf-8")
        consulta = cargar(ruta)
        base = base_de(consulta)
        db = get_db(base, atlas=args.atlas)
        if not args.atlas:
            verificar_base(db, base)
    except (EjercicioNoEncontrado, ErrorDeSintaxis, BaseVacia, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except PyMongoError as e:
        print(
            f"No me pude conectar a Mongo ({e.__class__.__name__}). ¿Está corriendo? cd entorno && docker compose up -d mongo",
            file=sys.stderr,
        )
        return 1

    meta = metadatos(texto)
    print(f"{NEGRITA}{meta['titulo'] or ruta.name}{FIN}  {GRIS}[{base} @ {'Atlas' if args.atlas else 'local'}]{FIN}")
    if meta["enunciado"]:
        print(f"{GRIS}{meta['enunciado']}{FIN}")
    print(f"\n{codigo_visible(texto)}\n")
    if args.pymongo:
        print(f"{GRIS}# pymongo equivalente:{FIN}\n{como_pymongo(consulta)}\n")

    try:
        if args.etapas and consulta.tipo == "aggregate":
            for k, etapa in enumerate(consulta.pipeline, 1):
                nombre = next(iter(etapa))
                imprimir(ejecutar(consulta, db, etapas=k), maximo=min(args.max, 5), titulo=f"-- Etapa {k}: {nombre}")
        else:
            t0 = time.perf_counter()
            filas = ejecutar(consulta, db)
            imprimir(filas, maximo=args.max)
            print(f"{GRIS}{(time.perf_counter() - t0) * 1000:.0f} ms{FIN}")
    except PyMongoError as e:
        print(f"Mongo rechazó la consulta: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
