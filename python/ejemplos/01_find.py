"""Consultas find del taller, escritas en pymongo.

    python3 python/ejemplos/01_find.py

Lo que cambia respecto de mongosh:
  - las claves van entre comillas ("user_id", "$in"): son dicts de Python;
  - las regex son re.compile(...) (o {"$regex": ...});
  - sort recibe (campo, dirección) en vez de un documento;
  - find devuelve un cursor perezoso: no trae nada hasta que se itera.
"""

import os
import re

from pymongo import DESCENDING, MongoClient
from pymongo.database import Database

from modelo import Tweet

# Local (docker) por defecto. Para la base del taller en Atlas, con la URL que comparte la cátedra:
#   MONGO_URI="$ATLAS_URI" python3 ...
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")


# =============================================================================
# Consultas: solo hablan con Mongo y devuelven datos. Sin prints.
# =============================================================================


def tweets_de_usuario(db: Database, user_id: str) -> list[Tweet]:
    """E1 - mongosh: db.tweets.find({ user_id: "188068413" })"""
    cursor = db.tweets.find({"user_id": user_id})
    return [Tweet.desde_documento(doc) for doc in cursor]  # cada doc es un dict


def retweets_por_pais(db: Database, paises: list[str]) -> list[dict]:
    """E3 - mongosh: db.tweets.find({ "place.country": { $in: [...] } },
                                    { _id: 0, "place.country": 1, retweet_count: 1 })

    Con proyección el documento viene recortado: devolvemos dicts, no Tweets
    (Tweet.desde_documento daría KeyError por los campos que faltan).
    """
    filtro = {"place.country": {"$in": paises}}
    proyeccion = {"_id": 0, "place.country": 1, "retweet_count": 1}
    return list(db.tweets.find(filtro, proyeccion))


def usuarios_llamados(db: Database, nombre: str) -> list[str]:
    """E6 - mongosh: db.tweets.distinct("user.screen_name", { "user.name": /Juan/ })"""
    return db.tweets.distinct("user.screen_name", {"user.name": re.compile(nombre)})


def top_retweets(db: Database, n: int = 10) -> list[Tweet]:
    """E7 - mongosh: db.tweets.find({}).sort({ retweet_count: -1 }).limit(10)"""
    cursor = (
        db.tweets.find({})
        .sort("retweet_count", DESCENDING)  # o .sort([("retweet_count", -1)])
        .limit(n)
    )
    return [Tweet.desde_documento(doc) for doc in cursor]


# =============================================================================
# Mostrar: llama a las consultas e imprime.
# =============================================================================


def titulo(t: str) -> None:
    print(f"\n-- {t}")


def main() -> None:
    db = MongoClient(MONGO_URI).tweets

    titulo("E1 - find con igualdad -> objetos Tweet")
    tweets = tweets_de_usuario(db, "188068413")
    print(f"{len(tweets)} tweets de @{tweets[0].usuario.screen_name}")
    for t in tweets[:3]:
        print(" ", t)
    print(f"  de esos, {sum(t.es_retweet for t in tweets)} son retweets")

    titulo("E3 - $in + proyección (dicts recortados, no Tweets)")
    filas = retweets_por_pais(db, ["Argentina", "Brasil"])
    for fila in filas[:3]:
        print(" ", fila)
    print(f"  total: {len(filas)}")

    titulo("E6 - regex con re.compile")
    juanes = usuarios_llamados(db, "Juan")
    print(f"  {len(juanes)} usuarios distintos, por ejemplo: {juanes[:5]}")

    titulo("E7 - sort + limit (el cursor se arma antes de ir a la base)")
    for t in top_retweets(db, 10):
        print(" ", t)


if __name__ == "__main__":
    main()
