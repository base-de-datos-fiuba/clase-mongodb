"""Encontrar, leer y ejecutar los ejercicios (.ts) contra una base."""

from __future__ import annotations

import re
from pathlib import Path

from pymongo.database import Database

from clase.mongosh import Consulta, parsear

RAIZ = Path(__file__).resolve().parents[2]  # raíz del repo (python/clase/ejercicios.py)
RESUELTOS = RAIZ / "consultas"
LIBRE = RESUELTOS / "libre.ts"

# colección -> base donde vive
BASES = {"tweets": "tweets", "publicaciones": "pizzagram"}

COMO_CARGAR = {
    "tweets": "python3 entorno/descargar_tweets.py && cd entorno && docker compose run --rm seed",
    "pizzagram": "python3 entorno/generar_pizzagram.py && cd entorno && docker compose run --rm seed",
}


class EjercicioNoEncontrado(Exception):
    pass


class BaseVacia(Exception):
    pass


def resueltos() -> list[Path]:
    """Los ejercicios resueltos (todos los .ts de consultas/ menos libre.ts)."""
    return [p for p in sorted(RESUELTOS.rglob("*.ts")) if p != LIBRE]


def disponibles() -> list[str]:
    nombres = []
    for p in resueltos():
        rel = p.relative_to(RESUELTOS).with_suffix("")
        nombres.append(str(rel.parent / rel.name.split("_")[0]) if rel.parent != Path(".") else rel.name.split("_")[0])
    return nombres


def _normalizar(codigo: str) -> str:
    m = re.fullmatch(r"([eE])(\d+)", codigo)
    if m:
        return f"E{int(m.group(2)):02d}"
    if codigo.lower() in ("p", "pizzagram"):
        return "P"
    return codigo


def resolver(nombre: str) -> Path:
    """'E1' / 'e01' / 'P' / 'pizzagram' / 'errores/E03' / 'libre' / una ruta a un .ts."""
    if nombre in ("libre", "libre.ts"):
        return LIBRE
    ruta = Path(nombre)
    if ruta.suffix == ".ts" and ruta.exists():
        return ruta.resolve()
    carpeta, _, codigo = nombre.rpartition("/")
    base = RESUELTOS / carpeta if carpeta else RESUELTOS
    codigo = _normalizar(codigo)
    candidatos = sorted(base.glob(f"{codigo}_*.ts")) + sorted(base.glob(f"{codigo}.ts"))
    if len(candidatos) == 1:
        return candidatos[0]
    lista = ", ".join(disponibles())
    raise EjercicioNoEncontrado(f"No encontré el ejercicio '{nombre}'. Disponibles: {lista}, libre")


def cargar(path: Path) -> Consulta:
    return parsear(Path(path).read_text(encoding="utf-8"))


def base_de(consulta: Consulta) -> str:
    return BASES.get(consulta.coleccion, "tweets")


def esperados(base: str) -> int | None:
    """Cantidad de documentos que debería tener cada base cargada completa."""
    if base == "tweets":
        return 100000
    if base == "pizzagram":
        archivo = RAIZ / "entorno" / "datos" / "pizzagram.json"
        if archivo.exists():
            import json

            return len(json.loads(archivo.read_text(encoding="utf-8")))
    return None


def verificar_base(db: Database, base: str) -> None:
    colecciones = {"tweets": "tweets", "pizzagram": "publicaciones"}
    col = colecciones.get(base)
    if not col:
        return
    n = db[col].estimated_document_count()
    if n == 0:
        raise BaseVacia(
            f"La colección '{col}' de la base '{base}' está vacía: la consulta devolvería [] sin avisar.\n"
            f"Cargala con: {COMO_CARGAR[base]}"
        )
    esperado = esperados(base)
    if esperado and n != esperado:
        raise BaseVacia(
            f"La colección '{col}' de la base '{base}' está incompleta: tiene {n} documentos y debería tener {esperado}.\n"
            f"Los resultados serían números creíbles pero incorrectos. Recargala con: {COMO_CARGAR[base]}"
        )


def ejecutar(consulta: Consulta, db: Database, etapas: int | None = None) -> list[dict]:
    col = db[consulta.coleccion]
    if consulta.tipo == "aggregate":
        pipeline = consulta.pipeline if etapas is None else consulta.pipeline[:etapas]
        return list(col.aggregate(pipeline))
    if consulta.contar:
        return [
            {
                "count": col.count_documents(
                    consulta.filtro, skip=consulta.skip, **({"limit": consulta.limite} if consulta.limite else {})
                )
            }
        ]
    cursor = col.find(consulta.filtro, consulta.proyeccion)
    if consulta.orden:
        cursor = cursor.sort(consulta.orden)
    if consulta.skip:
        cursor = cursor.skip(consulta.skip)
    if consulta.limite:
        cursor = cursor.limit(consulta.limite)
    return list(cursor)


def como_pymongo(consulta: Consulta) -> str:
    """La llamada pymongo equivalente, para mostrar 'desde el código'."""
    from pprint import pformat

    c = f"db.{consulta.coleccion}"
    if consulta.tipo == "aggregate":
        return f"list({c}.aggregate(\n{pformat(consulta.pipeline, indent=2, sort_dicts=False)}\n))"
    if consulta.contar:
        return f"{c}.count_documents({pformat(consulta.filtro, sort_dicts=False)})"
    s = f"{c}.find({pformat(consulta.filtro, sort_dicts=False)}"
    if consulta.proyeccion is not None:
        s += f", {pformat(consulta.proyeccion, sort_dicts=False)}"
    s += ")"
    if consulta.orden:
        s += f".sort({consulta.orden!r})"
    if consulta.skip:
        s += f".skip({consulta.skip})"
    if consulta.limite:
        s += f".limit({consulta.limite})"
    return f"list({s})"
