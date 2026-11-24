"""Agregaciones del taller, escritas en pymongo.

    python3 python/ejemplos/02_aggregate.py

El pipeline es una lista de Python con un dict por etapa. Como es código,
se puede armar por partes, reutilizar etapas y testear cada una.
"""

import os

from pymongo import MongoClient
from pymongo.database import Database

# Local (docker) por defecto. Para la base del taller en Atlas, con la URL que comparte la cátedra:
#   MONGO_URI="$ATLAS_URI" python3 ...
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")


# =============================================================================
# Consultas: solo hablan con Mongo y devuelven datos. Sin prints.
# =============================================================================

# E9 - mongosh: db.tweets.aggregate([ ...estas mismas etapas... ])
TOP_HASHTAGS = [
    {"$unwind": "$entities.hashtags"},
    {"$group": {"_id": "$entities.hashtags.text", "cantidad": {"$sum": 1}}},
    {"$sort": {"cantidad": -1}},
    {"$limit": 10},
]


def top_hashtags(db: Database, lang: str | None = None) -> list[dict]:
    """E9. Si se pasa lang, se agrega un $match adelante: el pipeline se arma por partes."""
    filtro = [{"$match": {"lang": lang}}] if lang else []
    return list(db.tweets.aggregate(filtro + TOP_HASHTAGS))


def hashtags_sin_pesos(db: Database) -> list[dict]:
    """El error del $ que falta: para Python y para Mongo es solo un string más."""
    mal = [
        {"$unwind": "$entities.hashtags"},
        {"$group": {"_id": "entities.hashtags.text", "cantidad": {"$sum": 1}}},  # falta el $
    ]
    return list(db.tweets.aggregate(mal))  # un solo grupo, sin error


def promedio_argentina_vs_resto(db: Database) -> list[dict]:
    """E11 - _id calculado con $cond."""
    pipeline = [
        {
            "$group": {
                "_id": {"$cond": [{"$eq": ["$place.country", "Argentina"]}, "Argentina", "resto"]},
                "promedio_retweets": {"$avg": "$retweet_count"},
                "tweets": {"$sum": 1},
            }
        }
    ]
    return list(db.tweets.aggregate(pipeline))


# =============================================================================
# Mostrar: llama a las consultas e imprime.
# =============================================================================


def titulo(t: str) -> None:
    print(f"\n-- {t}")


def main() -> None:
    db = MongoClient(MONGO_URI).tweets

    titulo("E9 - $unwind + $group")
    for fila in top_hashtags(db):
        print(f"  #{fila['_id']:<25} {fila['cantidad']}")

    titulo("E9 bis - mismo pipeline, solo tweets en español ($match agregado adelante)")
    print("  ", [f"#{f['_id']}" for f in top_hashtags(db, lang="es")][:5])

    titulo("Error: 'entities.hashtags.text' sin $ agrupa todo en un solo grupo")
    print("  ", hashtags_sin_pesos(db))

    titulo("E11 - _id calculado con $cond")
    for fila in promedio_argentina_vs_resto(db):
        print(f"  {fila['_id']:<10} {fila['promedio_retweets']:>10.2f} RT promedio en {fila['tweets']} tweets")


if __name__ == "__main__":
    main()
