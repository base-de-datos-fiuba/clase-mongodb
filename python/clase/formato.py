"""Mostrar resultados en la terminal de forma legible."""

from __future__ import annotations

from bson.json_util import RELAXED_JSON_OPTIONS, dumps

GRIS, VERDE, AMARILLO, NEGRITA, FIN = "\033[90m", "\033[92m", "\033[93m", "\033[1m", "\033[0m"


def doc_a_texto(doc: dict) -> str:
    return dumps(doc, json_options=RELAXED_JSON_OPTIONS, indent=2, ensure_ascii=False)


def imprimir(filas: list[dict], maximo: int = 20, titulo: str | None = None) -> None:
    if titulo:
        print(f"\n{NEGRITA}{titulo}{FIN}")
    for doc in filas[:maximo]:
        print(doc_a_texto(doc))
    resto = len(filas) - maximo
    if resto > 0:
        print(f"{GRIS}... y {resto} documentos más (usá --max N){FIN}")
    color = AMARILLO if not filas else VERDE
    print(f"{color}{len(filas)} documento(s){FIN}")
    if not filas:
        print(f"{AMARILLO}Ojo: [] no es un error para Mongo. ¿El campo existe y tiene esa forma?{FIN}")
