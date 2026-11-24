"""Documentos vs. tablas, vistos desde el código.

    python3 python/demo_documentos.py

Muestra cuatro cosas que se sienten distinto al programar contra Mongo:
  1. Un documento ES un dict: no hay JOIN ni ORM en el medio.
  2. Cada documento puede tener campos distintos (retweeted_status sí / no).
  3. El costo: un typo en un campo no es un error, es un resultado vacío.
  4. Agregar un campo nuevo no requiere migración.
"""

from clase.conexion import cliente, get_db

N, G, F = "\033[1m", "\033[90m", "\033[0m"


def titulo(t: str) -> None:
    print(f"\n{N}-- {t}{F}")


def main() -> None:
    tweets = get_db("tweets").tweets

    titulo("1. Un tweet es un dict de Python")
    t = tweets.find_one({"place.country": "Argentina", "entities.hashtags.0": {"$exists": True}})
    print(f"t['user']['name']             -> {t['user']['name']!r}")
    print(f"t['place']['country']         -> {t['place']['country']!r}")
    print(f"[h['text'] for h in hashtags] -> {[h['text'] for h in t['entities']['hashtags']]}")
    print(f"{G}En SQL: SELECT ... FROM tweets JOIN users ... JOIN hashtags ... y armar el objeto a mano (o un ORM).{F}")

    titulo("2. Documentos de la misma colección con campos distintos")
    total = tweets.estimated_document_count()
    con_rt = tweets.count_documents({"retweeted_status": {"$exists": True}})
    print(f"{con_rt} de {total} tweets tienen 'retweeted_status' ({con_rt / total:.0%})")
    for doc in tweets.find({}, {"retweeted_status": 1}).limit(4):
        rt = doc.get("retweeted_status")  # .get(): puede no estar
        print(f"  {doc['_id']}: {'retweet de @' + rt['user']['screen_name'] if rt else 'tweet original'}")
    print(f"{G}En SQL: columnas que casi siempre son NULL, o una tabla aparte + JOIN.{F}")

    titulo("3. El costo: los errores de nombre son silenciosos")
    for filtro in ({"language": "es"}, {"geo": "Argentina"}, {"lang": "es"}):
        print(f"  find({filtro}) -> {tweets.count_documents(filtro)} documentos")
    print(f"{G}En SQL: SELECT * FROM tweets WHERE language = 'es'  ->  ERROR: column \"language\" does not exist{F}")
    print(f"{G}En Mongo la validación del esquema pasa a ser responsabilidad de la aplicación (o de $jsonSchema).{F}")

    titulo("4. Agregar un campo sin migración")
    demo = cliente()["demo"].tweets
    demo.drop()
    demo.insert_many(
        [
            {"_id": 1, "texto": "tweet viejo"},
            {"_id": 2, "texto": "tweet nuevo", "es_sospechoso": True},  # campo nuevo, solo en este
        ]
    )
    for doc in demo.find():
        print(f"  {doc}")
    print(f"{G}En SQL: ALTER TABLE tweets ADD COLUMN es_sospechoso boolean;  (y en tablas grandes, puede bloquear){F}")
    cliente().drop_database("demo")


if __name__ == "__main__":
    main()
