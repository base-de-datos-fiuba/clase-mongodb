"""Traduce una consulta escrita en sintaxis mongosh (archivo .ts) a pymongo.

Soporta lo que usamos en clase:
  db.<coleccion>.find(<filtro>[, <proyeccion>]) [.sort({...})] [.skip(n)] [.limit(n)] [.count()]
  db.<coleccion>.aggregate([ ...etapas... ])

Literales: claves sin comillas, comillas simples, comas finales, comentarios,
regex /patron/flags, ISODate("...") y new Date("...").
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import timezone

import json5
from bson import json_util
from bson.json_util import JSONOptions

_JSON_OPTS = JSONOptions(tz_aware=True, tzinfo=timezone.utc)
_ANTES_DE_REGEX = set(":,[({!&|=?")


class ErrorDeSintaxis(Exception):
    pass


@dataclass
class Consulta:
    coleccion: str
    tipo: str  # "find" | "aggregate"
    filtro: dict = field(default_factory=dict)
    proyeccion: dict | None = None
    orden: list[tuple[str, int]] = field(default_factory=list)
    skip: int = 0
    limite: int | None = None
    contar: bool = False
    pipeline: list[dict] = field(default_factory=list)


# ---------------------------------------------------------------- limpieza


def _limpiar(texto: str) -> str:
    """Saca comentarios y convierte regex / fechas a Extended JSON.

    Conserva los saltos de línea para poder reportar el número de línea.
    """
    out: list[str] = []
    i, n = 0, len(texto)
    while i < n:
        c = texto[i]
        if c in "\"'`":
            j = _fin_de_string(texto, i)
            out.append(texto[i : j + 1])
            i = j + 1
        elif texto.startswith("//", i):
            j = texto.find("\n", i)
            i = n if j == -1 else j
        elif texto.startswith("/*", i):
            j = texto.find("*/", i + 2)
            if j == -1:
                raise ErrorDeSintaxis(f"Comentario /* sin cerrar (línea {_linea(texto, i)})")
            out.append("\n" * texto.count("\n", i, j))
            i = j + 2
        elif c == "/" and _ultimo_significativo(out) in _ANTES_DE_REGEX:
            j = i + 1
            while j < n and texto[j] != "/":
                if texto[j] == "\\":
                    j += 1
                if j >= n or texto[j] == "\n":
                    raise ErrorDeSintaxis(f"Regex sin cerrar (línea {_linea(texto, i)})")
                j += 1
            patron = texto[i + 1 : j]
            k = j + 1
            while k < n and texto[k].isalpha():
                k += 1
            flags = texto[j + 1 : k]
            out.append(json.dumps({"$regularExpression": {"pattern": patron, "options": flags}}))
            i = k
        else:
            m = re.compile(r"(?:ISODate|new\s+Date)\(\s*([\"'])(.*?)\1\s*\)").match(texto, i)
            if m and (i == 0 or not (texto[i - 1].isalnum() or texto[i - 1] in "_$")):
                out.append(json.dumps({"$date": m.group(2)}))
                i = m.end()
            else:
                out.append(c)
                i += 1
    return "".join(out)


def _fin_de_string(texto: str, i: int) -> int:
    q, j = texto[i], i + 1
    while j < len(texto):
        if texto[j] == "\\":
            j += 2
            continue
        if texto[j] == q:
            return j
        j += 1
    raise ErrorDeSintaxis(f"String sin cerrar (línea {_linea(texto, i)})")


def _ultimo_significativo(partes: list[str]) -> str:
    for p in reversed(partes):
        s = p.rstrip()
        if s:
            return s[-1]
    return ","  # inicio del texto


def _linea(texto: str, pos: int) -> int:
    return texto.count("\n", 0, pos) + 1


# ---------------------------------------------------------------- parseo


def _argumentos(texto: str, abre: int) -> tuple[str, int]:
    """Devuelve el contenido entre el '(' en `abre` y su ')' y la posición del ')'."""
    prof, j = 0, abre
    while j < len(texto):
        c = texto[j]
        if c in "\"'`":
            j = _fin_de_string(texto, j)
        elif c in "([{":
            prof += 1
        elif c in ")]}":
            prof -= 1
            if prof == 0:
                if c != ")":
                    break
                return texto[abre + 1 : j], j
        j += 1
    raise ErrorDeSintaxis(f"Paréntesis o llaves sin balancear (línea {_linea(texto, abre)})")


def _separar_top(args: str) -> list[str]:
    partes, prof, inicio, j = [], 0, 0, 0
    while j < len(args):
        c = args[j]
        if c in "\"'`":
            j = _fin_de_string(args, j)
        elif c in "([{":
            prof += 1
        elif c in ")]}":
            prof -= 1
        elif c == "," and prof == 0:
            partes.append(args[inicio:j])
            inicio = j + 1
        j += 1
    partes.append(args[inicio:])
    return [p for p in partes if p.strip()]


def _valor(fuente: str, texto: str, offset: int):
    try:
        crudo = json5.loads(fuente)
    except ValueError as e:
        raise ErrorDeSintaxis(
            f"No pude leer el argumento que empieza en la línea {_linea(texto, offset)}: {e}"
        ) from None
    return json_util.loads(json.dumps(crudo), json_options=_JSON_OPTS)


def parsear(texto: str) -> Consulta:
    limpio = _limpiar(texto)
    m = re.search(r"\bdb\s*\.\s*([A-Za-z_][\w]*)\s*\.\s*(find|aggregate)\s*\(", limpio)
    if not m:
        raise ErrorDeSintaxis(
            "No encontré ninguna consulta db.<coleccion>.find(...) ni db.<coleccion>.aggregate([...])"
        )
    consulta = Consulta(coleccion=m.group(1), tipo=m.group(2))
    abre = m.end() - 1
    args, cierra = _argumentos(limpio, abre)
    partes = _separar_top(args)

    if consulta.tipo == "aggregate":
        if len(partes) != 1:
            raise ErrorDeSintaxis(f"aggregate recibe una lista de etapas (línea {_linea(limpio, abre)})")
        pipeline = _valor(partes[0], limpio, abre)
        if not isinstance(pipeline, list):
            raise ErrorDeSintaxis(f"aggregate recibe una lista [ ... ] (línea {_linea(limpio, abre)})")
        consulta.pipeline = pipeline
    else:
        if len(partes) > 2:
            raise ErrorDeSintaxis(f"find recibe a lo sumo filtro y proyección (línea {_linea(limpio, abre)})")
        if partes:
            consulta.filtro = _valor(partes[0], limpio, abre)
        if len(partes) == 2:
            consulta.proyeccion = _valor(partes[1], limpio, abre)

    # métodos encadenados
    pos = cierra + 1
    cadena = re.compile(r"\s*\.\s*(\w+)\s*\(")
    while True:
        mc = cadena.match(limpio, pos)
        if not mc:
            break
        metodo, abre = mc.group(1), mc.end() - 1
        arg, cierra = _argumentos(limpio, abre)
        if consulta.tipo == "aggregate" and metodo not in ("toArray", "pretty"):
            etapa = {"sort": "$sort", "limit": "$limit", "skip": "$skip", "count": "$count"}.get(metodo, "una etapa")
            raise ErrorDeSintaxis(
                f".{metodo}() después de aggregate no se aplica acá: agregalo como etapa del pipeline "
                f"({etapa}) (línea {_linea(limpio, abre)})"
            )
        if metodo == "sort":
            consulta.orden = list(_valor(arg, limpio, abre).items())
        elif metodo in ("limit", "skip"):
            v = _valor(arg, limpio, abre)
            setattr(consulta, "limite" if metodo == "limit" else "skip", int(v))
        elif metodo in ("count", "countDocuments"):
            consulta.contar = True
        elif metodo in ("toArray", "pretty"):
            pass
        else:
            raise ErrorDeSintaxis(f"Método .{metodo}() no soportado (línea {_linea(limpio, abre)})")
        pos = cierra + 1

    resto = limpio[pos:].strip().rstrip(";").strip()
    if resto:
        raise ErrorDeSintaxis(f"Sobra texto después de la consulta (línea {_linea(limpio, pos)}): {resto[:40]!r}")
    return consulta


# ---------------------------------------------------------------- metadatos

_CABECERA = re.compile(r"^\s*/\*\*.*?\*/\s*", re.DOTALL)
_DECLARE = re.compile(r"^\s*declare\s+const\s+db\s*:\s*any\s*;?.*$\n?", re.MULTILINE)


def metadatos(texto: str) -> dict:
    datos = {"titulo": "", "enunciado": "", "concepto": ""}
    m = _CABECERA.match(texto)
    if m:
        claves = {"título": "titulo", "titulo": "titulo", "enunciado": "enunciado", "concepto": "concepto"}
        actual = None
        for linea in m.group(0).splitlines():
            linea = linea.strip().lstrip("/*").rstrip("*/").strip()
            mm = re.match(r"(\w+):\s*(.*)", linea)
            if mm and mm.group(1).lower() in claves:
                actual = claves[mm.group(1).lower()]
                datos[actual] = mm.group(2).strip()
            elif actual and linea:
                datos[actual] += " " + linea
    return datos


def codigo_visible(texto: str) -> str:
    return _DECLARE.sub("", _CABECERA.sub("", texto, count=1)).strip()
