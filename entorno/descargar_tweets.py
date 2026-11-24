"""Descarga la colección de tweets del taller (Atlas) a entorno/datos/tweets.jsonl.gz.

Se corre una sola vez. Usa Extended JSON canónico para no perder tipos
(fechas, enteros de 64 bits) al volver a cargarlo en el Mongo local.

    python3 entorno/descargar_tweets.py
"""

import gzip
import os
import sys
import time
from pathlib import Path

from bson.json_util import CANONICAL_JSON_OPTIONS, dumps, loads
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# La URL de Atlas (con usuario y clave) no se versiona: la comparte la cátedra.
#   export ATLAS_URI='mongodb+srv://...'  &&  python3 entorno/descargar_tweets.py
ATLAS_URI = os.environ.get("ATLAS_URI")

DESTINO = Path(__file__).resolve().parent / "datos" / "tweets.jsonl.gz"


def _parcial(tmp: Path) -> list[str]:
    """Líneas completas de una descarga anterior interrumpida (si existe)."""
    lineas: list[str] = []
    if not tmp.exists():
        return lineas
    try:
        with gzip.open(tmp, "rt", encoding="utf-8") as f:
            for linea in f:
                if linea.endswith("\n"):
                    lineas.append(linea)
    except (EOFError, OSError):
        pass  # el archivo quedó cortado: nos quedamos con lo que se pudo leer
    return lineas


def main() -> None:
    if not ATLAS_URI:
        sys.exit(
            "Falta la variable de entorno ATLAS_URI con la URL de Atlas que comparte la cátedra.\n"
            "Definila y volvé a correr:  export ATLAS_URI='mongodb+srv://...'"
        )
    tweets = MongoClient(ATLAS_URI, serverSelectionTimeoutMS=15000).tweets.tweets
    total = tweets.estimated_document_count()
    DESTINO.parent.mkdir(exist_ok=True)
    tmp = DESTINO.with_suffix(".tmp")
    i, ultimo, intentos = 0, None, 0
    lineas = _parcial(tmp)
    if lineas:
        i, ultimo = len(lineas), loads(lineas[-1])["_id"]
        print(f"  retomo una descarga anterior desde {i}", flush=True)
    with gzip.open(tmp, "wt", encoding="utf-8") as f:
        f.writelines(lineas)
        while True:
            filtro = {"_id": {"$gt": ultimo}} if ultimo is not None else {}
            try:
                # Ordenado por _id: si se corta la conexión, retomamos desde el último descargado.
                for doc in tweets.find(filtro).sort("_id", 1).batch_size(2000):
                    f.write(dumps(doc, json_options=CANONICAL_JSON_OPTIONS) + "\n")
                    ultimo, i = doc["_id"], i + 1
                    if i % 10000 == 0:
                        print(f"  {i}/{total}", flush=True)
                break
            except PyMongoError as e:
                intentos += 1
                if intentos > 20:
                    raise SystemExit(f"Se cortó demasiadas veces. Volvé a correr el script: retoma desde {i}.") from e
                print(f"  se cortó la conexión ({e.__class__.__name__}); reintento {intentos}/20 desde {i}", flush=True)
                time.sleep(min(3 * intentos, 15))
    tmp.replace(DESTINO)
    print(f"tweets: {i} documentos -> {DESTINO}")


if __name__ == "__main__":
    main()
