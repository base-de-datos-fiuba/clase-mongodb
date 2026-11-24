# Clase MongoDB — Base de Datos (FIUBA)

Material de la clase de MongoDB: la presentación, las consultas resueltas y un entorno local para practicarlas.

```
presentacion/clase-mongo.html   la diapo (abrir con doble clic; funciona sin internet)
consultas/                      ejercicios resueltos y comentados (.ts, sintaxis mongosh)
  errores/                      errores frecuentes de entregas, para comparar
  libre.ts                      consulta libre para probar lo que quieras
python/
  execute_query.py              corre cualquier .ts con pymongo
  ejemplos/                     los ejercicios escritos en pymongo, con el tweet modelado como clase
  demo_documentos.py            documentos vs. tablas, vistos desde el código
entorno/                        Mongo en docker + scripts para cargar los datos
```

## Sin instalar nada

Las consultas de `consultas/` se pueden pegar en `mongosh` o Compass (todo menos la línea
`declare const db: any;`, que es solo para el editor) contra la base del taller en Atlas
(base `tweets`, solo lectura). La URL de conexión la comparte la cátedra: no está en este repo.

Para usarla desde los scripts, definila como variable de entorno:

```bash
export ATLAS_URI='mongodb+srv://...'     # la URL que comparte la cátedra
```

Pizzagram **no** está en Atlas: para practicarlo hace falta el entorno local.

## Entorno local

Requisitos: Docker y Python 3.10+.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r python/requirements.txt

python3 entorno/descargar_tweets.py        # (necesita ATLAS_URI) baja los 100k tweets del taller (una sola vez; si se corta, retoma)
cd entorno
docker compose up -d mongo                 # Mongo en localhost:27017
docker compose run --rm seed               # carga los tweets y Pizzagram en la base
cd ..
```

`entorno/datos/pizzagram.json` ya viene generado (`python3 entorno/generar_pizzagram.py` lo regenera).

## Correr consultas

```bash
python3 python/execute_query.py                   # corre consultas/libre.ts
python3 python/execute_query.py E9                # consultas/E09_hashtags.ts
python3 python/execute_query.py P --etapas        # Pizzagram, mostrando la salida de cada etapa
python3 python/execute_query.py E3 --atlas        # contra la base del taller en Atlas (necesita ATLAS_URI)
python3 python/execute_query.py E9 --pymongo      # muestra también la llamada pymongo equivalente
python3 python/execute_query.py errores/E03       # una versión con error
```

Sin Python local: `cd entorno && docker compose run --rm cli E9`.

`execute_query.py` traduce los `.ts` a pymongo (soporta `find` con `sort`/`skip`/`limit`/`count` y `aggregate`).

## Ejemplos en pymongo

```bash
python3 python/ejemplos/01_find.py        # E1, E3, E6, E7: find, proyección, regex, sort/limit
python3 python/ejemplos/02_aggregate.py   # E9, E11: pipelines como listas de Python (y el $ que falta)
python3 python/ejemplos/03_abm.py         # insert / update ($set, $inc, $unset, upsert) / delete con el modelo
python3 python/demo_documentos.py         # pros y contras de los documentos desde el código
```

Cada ejemplo separa las **consultas** (funciones que solo hablan con Mongo) de lo que se **muestra** (`main()`).
`python/ejemplos/modelo.py` modela el tweet como dataclasses (`Tweet`, `Usuario`): el esquema que Mongo no tiene
vive en el código. Ojo: el tweet original embebido en `retweeted_status` usa `id_str` y `created_at` como string,
a diferencia de la raíz (`_id`, fecha `Date`); el modelo absorbe las dos formas.

## Bases

| Base | Colección | Contenido |
|------|-----------|-----------|
| `tweets` | `tweets` | 100.000 tweets del 26/06/2019 (copia de la base del taller) |
| `pizzagram` | `publicaciones` | mock del ejercicio de parcial, con bots plantados |
