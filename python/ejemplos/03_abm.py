"""Altas, bajas y modificaciones con el modelo Tweet.

    python3 python/ejemplos/03_abm.py

Trabaja sobre una base "demo_abm" que se crea y se borra al final:
no toca los tweets del taller.
"""

import os
from datetime import datetime, timezone

from pymongo import MongoClient
from pymongo.collection import Collection

from modelo import Tweet, Usuario

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")  # necesita escribir: solo local


# =============================================================================
# Operaciones: solo hablan con Mongo y devuelven datos. Sin prints.
# =============================================================================


def insertar(col: Collection, tweet: Tweet) -> str:
    """Alta: objeto -> documento -> insert_one. Devuelve el _id."""
    return col.insert_one(tweet.a_documento()).inserted_id


def sumar_retweets_y_marcar(col: Collection, tweet_id: str, cantidad: int) -> None:
    """Modificación parcial: $inc y $set tocan esos campos, no reemplazan el documento."""
    col.update_one({"_id": tweet_id}, {"$inc": {"retweet_count": cantidad}, "$set": {"es_sospechoso": True}})


def desmarcar_sospechosos(col: Collection) -> int:
    """$unset en todos los que matchean. Devuelve cuántos se modificaron."""
    return col.update_many({"es_sospechoso": True}, {"$unset": {"es_sospechoso": ""}}).modified_count


def upsert_texto(col: Collection, tweet_id: str, texto: str):
    """update con upsert: si no existe, lo crea. Devuelve el _id creado (o None si ya existía)."""
    return col.update_one({"_id": tweet_id}, {"$set": {"full_text": texto}}, upsert=True).upserted_id


def borrar(col: Collection, ids: list[str]) -> int:
    """Baja. Devuelve cuántos se borraron."""
    return col.delete_many({"_id": {"$in": ids}}).deleted_count


# =============================================================================
# Mostrar: arma los datos, llama a las operaciones e imprime.
# =============================================================================


def titulo(t: str) -> None:
    print(f"\n-- {t}")


def main() -> None:
    cliente = MongoClient(MONGO_URI)
    demo = cliente["demo_abm"].tweets
    demo.drop()

    titulo("insert_one con un Tweet armado en código")
    nuevo = Tweet(
        id="999",
        texto="Probando pymongo en la clase #MongoDB",
        creado=datetime.now(timezone.utc),
        lang="es",
        retweet_count=0,
        usuario=Usuario(id="1", nombre="Docente FIUBA", screen_name="docente"),
        hashtags=["MongoDB"],
    )
    print(f"  insertado con _id {insertar(demo, nuevo)!r}")

    real = Tweet.desde_documento(cliente["tweets"].tweets.find_one({"retweeted_status": {"$exists": True}}))
    insertar(demo, real)
    print(f"  copiado un retweet real: {real}")

    titulo("update_one con $inc y $set (no reemplaza el documento)")
    sumar_retweets_y_marcar(demo, "999", 10)
    print("  ", demo.find_one({"_id": "999"}, {"_id": 0, "retweet_count": 1, "es_sospechoso": 1}))
    print("   'es_sospechoso' no está en el modelo: Tweet.desde_documento lo ignora. El esquema lo decide el código.")

    titulo("update_many con $unset")
    print(f"  {desmarcar_sospechosos(demo)} documento(s) modificado(s)")

    titulo("update con upsert: si no existe, lo crea")
    print(f"  upserted_id = {upsert_texto(demo, '1000', 'creado por upsert')!r}")

    titulo("delete_many")
    print(f"  {borrar(demo, ['999', '1000'])} borrados; quedan {demo.count_documents({})}")

    cliente.drop_database("demo_abm")


if __name__ == "__main__":
    main()
