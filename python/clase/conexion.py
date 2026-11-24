"""Conexión a Mongo: local (docker) por defecto, o la base del taller en Atlas."""

import os

from pymongo import MongoClient
from pymongo.database import Database

LOCAL_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")

# La URL de Atlas (con usuario y clave) NO se versiona: la comparte la cátedra y se pasa por variable de entorno.
FALTA_ATLAS = (
    "Falta la variable de entorno ATLAS_URI con la URL de conexión a Atlas que comparte la cátedra.\n"
    "Definila antes de correr, por ejemplo:  export ATLAS_URI='mongodb+srv://...'"
)


def atlas_uri() -> str:
    uri = os.environ.get("ATLAS_URI")
    if not uri:
        raise ValueError(FALTA_ATLAS)
    return uri


_clientes: dict[str, MongoClient] = {}


def cliente(atlas: bool = False) -> MongoClient:
    uri = atlas_uri() if atlas else LOCAL_URI
    if uri not in _clientes:
        _clientes[uri] = MongoClient(uri, serverSelectionTimeoutMS=4000 if not atlas else 15000)
    return _clientes[uri]


def get_db(base: str, atlas: bool = False) -> Database:
    if atlas and base != "tweets":
        raise ValueError(f"En Atlas solo está la base 'tweets' (pediste '{base}'). Usá la base local.")
    return cliente(atlas)[base]
