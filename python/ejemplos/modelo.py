"""El tweet modelado en código.

Mongo no tiene esquema: el esquema vive acá. Esta clase decide qué campos son
obligatorios (si faltan, KeyError: un error FUERTE, como en SQL) y cuáles
opcionales (retweeted_status, place, location: .get() devuelve None).

Convertir documento <-> objeto es el trabajo que en SQL hace el ORM.

Ojo con los datos reales: el MISMO tweet tiene dos formas según dónde esté.
  - En la raíz de la colección:      _id,    created_at como Date.
  - Embebido en retweeted_status:     id_str, created_at como STRING ("Wed Jun 26 ...").
Nadie lo valida al guardar: lo descubre el código al leer. El modelo lo absorbe.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

FORMATO_TWITTER = "%a %b %d %H:%M:%S %z %Y"  # "Wed Jun 26 21:50:10 +0000 2019"


def _fecha(valor: datetime | str) -> datetime:
    """created_at viene como Date (raíz) o como string de Twitter (embebido)."""
    if isinstance(valor, str):
        return datetime.strptime(valor, FORMATO_TWITTER)
    return valor if valor.tzinfo else valor.replace(tzinfo=timezone.utc)


@dataclass
class Usuario:
    id: str
    nombre: str
    screen_name: str
    ubicacion: str | None = None  # opcional: muchos usuarios no la completan

    @classmethod
    def desde_documento(cls, doc: dict) -> Usuario:
        return cls(
            id=doc["id_str"],
            nombre=doc["name"],
            screen_name=doc["screen_name"],
            ubicacion=doc.get("location") or None,
        )

    def a_documento(self) -> dict:
        doc = {"id_str": self.id, "name": self.nombre, "screen_name": self.screen_name}
        if self.ubicacion:
            doc["location"] = self.ubicacion
        return doc


@dataclass
class Tweet:
    id: str
    texto: str
    creado: datetime
    lang: str
    retweet_count: int
    usuario: Usuario  # embebido: viene adentro del tweet
    hashtags: list[str] = field(default_factory=list)  # array de objetos -> lista de strings
    pais: str | None = None  # place es null en el 97% de los tweets
    retweet_de: Tweet | None = None  # retweeted_status: solo en los retweets

    @property
    def es_retweet(self) -> bool:
        return self.retweet_de is not None

    @classmethod
    def desde_documento(cls, doc: dict) -> Tweet:
        """Documento de Mongo (un dict) -> objeto. Los campos obligatorios usan [] a propósito."""
        place = doc.get("place") or {}
        original = doc.get("retweeted_status")
        return cls(
            id=doc["_id"] if "_id" in doc else doc["id_str"],  # raíz: _id - embebido: id_str
            texto=doc.get("full_text") or doc["text"],
            creado=_fecha(doc["created_at"]),
            lang=doc["lang"],
            retweet_count=doc["retweet_count"],
            usuario=Usuario.desde_documento(doc["user"]),
            hashtags=[h["text"] for h in doc.get("entities", {}).get("hashtags", [])],
            pais=place.get("country"),
            retweet_de=cls.desde_documento(original) if original else None,
        )

    def a_documento(self) -> dict:
        """Objeto -> documento, con los mismos nombres de campo que la colección."""
        doc = {
            "_id": self.id,
            "full_text": self.texto,
            "created_at": self.creado,
            "lang": self.lang,
            "retweet_count": self.retweet_count,
            "user_id": self.usuario.id,
            "user": self.usuario.a_documento(),
            "entities": {"hashtags": [{"text": h} for h in self.hashtags]},
            "place": {"country": self.pais} if self.pais else None,
        }
        if self.retweet_de:
            doc["retweeted_status"] = self.retweet_de.a_documento()
        return doc

    def __str__(self) -> str:
        rt = f" (RT de @{self.retweet_de.usuario.screen_name})" if self.es_retweet else ""
        return f"@{self.usuario.screen_name}{rt}: {self.texto[:60]!r} - {self.retweet_count} RT"
