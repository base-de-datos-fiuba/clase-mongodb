"""Carga entorno/datos/ en el Mongo local. Es idempotente: si ya está cargado, no hace nada.

cd entorno && docker compose run --rm seed     (o: python3 entorno/cargar_datos.py)
"""

import gzip
import json
import os
from pathlib import Path

from bson.json_util import loads
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")  # en docker: mongodb://mongo:27017

DATA = Path(__file__).resolve().parent / "datos"
LOTE = 5000


def _contar_lineas(path: Path) -> int:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return sum(1 for _ in f)


def cargar_tweets() -> None:
    archivo = DATA / "tweets.jsonl.gz"
    if not archivo.exists():
        print("tweets: falta entorno/datos/tweets.jsonl.gz -> corré primero: python3 entorno/descargar_tweets.py")
        return
    col = MongoClient(MONGO_URI).tweets.tweets
    esperado = _contar_lineas(archivo)
    if col.estimated_document_count() == esperado:
        print(f"tweets: {esperado} documentos (ya estaba cargado)")
        return
    col.drop()
    lote = []
    with gzip.open(archivo, "rt", encoding="utf-8") as f:
        for linea in f:
            lote.append(loads(linea))
            if len(lote) == LOTE:
                col.insert_many(lote, ordered=False)
                lote = []
    if lote:
        col.insert_many(lote, ordered=False)
    print(f"tweets: {col.estimated_document_count()} documentos")


def cargar_pizzagram() -> None:
    archivo = DATA / "pizzagram.json"
    if not archivo.exists():
        print("pizzagram: falta entorno/datos/pizzagram.json -> corré: python3 entorno/generar_pizzagram.py")
        return
    docs = json.loads(archivo.read_text(encoding="utf-8"))
    col = MongoClient(MONGO_URI).pizzagram.publicaciones
    col.drop()  # es chico: siempre se recarga para reflejar el archivo actual
    col.insert_many(docs)
    print(f"pizzagram: {len(docs)} publicaciones")


if __name__ == "__main__":
    cargar_tweets()
    cargar_pizzagram()
