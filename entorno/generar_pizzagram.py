"""Genera la base mock de Pizzagram (data/pizzagram.json) con bots plantados.

Regla del enunciado: una IP es bot en una pizzería si hizo EXACTAMENTE 10
comentarios en publicaciones de esa pizzería (en una o en varias).
Respuesta conocida: la IP 45.230.18.7 operó en 7 pizzerías.

    python3 entorno/generar_pizzagram.py
"""

from __future__ import annotations

import json
import random
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

IP_GANADORA = "45.230.18.7"
PIZZERIAS_GANADORA = 7

# ip -> en cuántas pizzerías opera (10 comentarios en cada una)
BOTS = {IP_GANADORA: 7, "181.15.99.200": 5, "200.123.4.56": 3, "190.0.66.6": 1}
BOT_UNA_PUBLICACION = "190.0.66.6"  # sus 10 comentarios caen en una sola publicación
IP_ONCE = "186.22.11.11"  # 11 comentarios en una pizzería: NO es bot
IP_REPARTIDA = "201.7.7.70"  # 10 comentarios repartidos en 4 pizzerías: NO es bot
IPS_PLANTADAS = set(BOTS) | {IP_ONCE, IP_REPARTIDA}

MAX_LEGITIMOS_POR_IP_PIZZERIA = 6

PIZZERIAS = [
    "La cuarteta de Guerrín",
    "El Cuartito de Almagro",
    "Pizzería Los Hornos",
    "Banchero del Sur",
    "La Mezzetta de Villa Crespo",
    "Las Cuartetas de Boedo",
    "El Palacio de la Muzza",
    "Pizzería Güerrín Jr.",
    "Fainá & Moscato",
    "La Continental del Barrio",
    "Don Zoilo Pizzas",
    "Pizza Piola",
    "El Fortín de la Fugazzeta",
    "Muzza Brava",
    "La Rueda Caballito",
    "Pizzería San Telmo",
    "Ñoqui & Pizza",
    "Horno de Barro Palermo",
    "La Grasa Feliz",
    "Pizzería El Obelisco",
    "Calabresa Club",
    "Napolitana Norte",
    "La Porteña de Flores",
    "Pizzas Don Mario",
    "El Molde de Oro",
    "La Fugazza Loca",
    "Pizza al Paso Once",
    "La Esquina de la Muzza",
    "Pizzería Villa Urquiza",
    "El Rey del Molde",
]

POSTEOS = [
    "Probaste la {g}? Este viernes 15% off!",
    "Nueva {g} a la piedra, venite!",
    "Hoy 2x1 en {g} hasta las 23",
    "La {g} de siempre, con más queso que nunca",
    "Martes de {g} + fainá de regalo",
    "Volvió la {g} de la casa",
]
GUSTOS = ["Calabresa", "Fugazzeta", "Napolitana", "Muzzarella", "Roquefort", "Jamón y morrones", "Provolone"]
LEGITIMOS = [
    "Espectacular la de roquefort también",
    "Me vino con cucaracha, un asco",
    "Muy rica pero tardó una hora",
    "La fainá estaba fría",
    "Mejor muzza de la zona",
    "Caro para lo que es",
    "Volvería sin dudar",
    "La masa estaba cruda",
    "Atención de diez",
    "Pedí delivery y llegó perfecta",
    "Meh, normalita",
]
BOT_TEXTOS = [
    "¡Increíble experiencia gastronómica, la mejor pizza que probé en mi vida!",
    "Sabores auténticos y atención de primer nivel. ¡Totalmente recomendable!",
    "Una explosión de sabor en cada bocado. ¡Cinco estrellas!",
    "Calidad premium, ingredientes frescos y un ambiente inmejorable.",
]
NOMBRES = [
    "pablitus",
    "zoe_mc_zoe_zoe",
    "juanpi",
    "lauchi",
    "mica.g",
    "el_tano",
    "sofi_r",
    "nachito",
    "caro99",
    "fede_bsas",
    "agus.m",
    "tincho",
    "valen",
    "rocio_p",
    "lucho",
    "mati_c",
    "flor",
    "gonza",
    "cami",
    "santi",
]


def _id(rng: random.Random) -> str:
    return "".join(rng.choice("0123456789ABCDEF") for _ in range(12))


def _ip(rng: random.Random) -> str:
    while True:
        ip = f"{rng.randint(100, 223)}.{rng.randint(0, 255)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}"
        if ip not in IPS_PLANTADAS:
            return ip


def _comentario(rng: random.Random, usuarios: list[str], ip: str, textos: list[str]) -> dict:
    return {"username": rng.choice(usuarios), "ip": ip, "texto": rng.choice(textos)}


def _bot_usuarios(rng: random.Random) -> list[str]:
    return [
        f"{rng.choice(['user', 'fan', 'foodie', 'pizza_lover'])}{rng.randint(1000, 9999)}"
        for _ in range(rng.randint(3, 6))
    ]


def generar(semilla: int = 2026) -> list[dict]:
    rng = random.Random(semilla)
    inicio = datetime(2025, 3, 1)
    pubs_por_pizzeria: dict[str, list[dict]] = {}
    for pizzeria in PIZZERIAS:
        pubs = []
        for _ in range(rng.randint(12, 20)):
            fecha = inicio + timedelta(seconds=rng.randint(0, 60 * 86400))
            pubs.append(
                {
                    "idPublicación": _id(rng),
                    "pizzeria": pizzeria,
                    "fecha_hora": fecha.strftime("%Y-%m-%d %H:%M:%S"),
                    "texto": rng.choice(POSTEOS).format(g=rng.choice(GUSTOS)),
                    "comentarios": [],
                }
            )
        pubs_por_pizzeria[pizzeria] = pubs

    # comentarios legítimos: ninguna IP llega a 10 en una pizzería
    pool = [_ip(rng) for _ in range(400)]
    conteo: Counter = Counter()
    for pizzeria, pubs in pubs_por_pizzeria.items():
        for p in pubs:
            for _ in range(rng.randint(0, 15)):
                ip = rng.choice(pool)
                if conteo[(ip, pizzeria)] >= MAX_LEGITIMOS_POR_IP_PIZZERIA:
                    continue
                conteo[(ip, pizzeria)] += 1
                p["comentarios"].append(_comentario(rng, NOMBRES, ip, LEGITIMOS))

    # bots: eligen 10 publicaciones al azar de cada pizzería que les compró comentarios
    for ip, n in BOTS.items():
        usuarios = _bot_usuarios(rng)
        for pizzeria in rng.sample(PIZZERIAS, n):
            pubs = pubs_por_pizzeria[pizzeria]
            destinos = [rng.choice(pubs)] * 10 if ip == BOT_UNA_PUBLICACION else rng.sample(pubs, 10)
            for p in destinos:
                p["comentarios"].append(_comentario(rng, usuarios, ip, BOT_TEXTOS))

    # distractor: 11 comentarios en una misma pizzería
    pubs = pubs_por_pizzeria[rng.choice(PIZZERIAS)]
    usuarios = _bot_usuarios(rng)
    for _ in range(11):
        rng.choice(pubs)["comentarios"].append(_comentario(rng, usuarios, IP_ONCE, BOT_TEXTOS))

    # distractor: 10 comentarios en total, repartidos 3+3+2+2 entre 4 pizzerías
    for pizzeria, k in zip(rng.sample(PIZZERIAS, 4), [3, 3, 2, 2]):
        for _ in range(k):
            rng.choice(pubs_por_pizzeria[pizzeria])["comentarios"].append(
                _comentario(rng, NOMBRES, IP_REPARTIDA, LEGITIMOS)
            )

    todas = [p for pubs in pubs_por_pizzeria.values() for p in pubs]
    for p in todas:
        rng.shuffle(p["comentarios"])
    rng.shuffle(todas)
    return todas


def bots_por_ip(publicaciones: list[dict]) -> dict[str, set[str]]:
    """Referencia en Python puro: ip -> pizzerías donde tiene exactamente 10 comentarios."""
    conteo = Counter((c["ip"], p["pizzeria"]) for p in publicaciones for c in p["comentarios"])
    bots: dict[str, set[str]] = defaultdict(set)
    for (ip, pizzeria), n in conteo.items():
        if n == 10:
            bots[ip].add(pizzeria)
    return dict(bots)


if __name__ == "__main__":
    destino = Path(__file__).resolve().parent / "datos" / "pizzagram.json"
    pubs = generar()
    destino.write_text(json.dumps(pubs, ensure_ascii=False, indent=1), encoding="utf-8")
    n = sum(len(p["comentarios"]) for p in pubs)
    print(f"pizzagram: {len(pubs)} publicaciones, {n} comentarios -> {destino}")
    print(f"respuesta esperada: {{'ip': '{IP_GANADORA}', 'cantidad_pizzerias': {PIZZERIAS_GANADORA}}}")
