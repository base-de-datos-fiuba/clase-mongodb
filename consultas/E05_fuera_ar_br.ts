/**
 * Título: E5 - Retweets fuera de Argentina y Brasil
 * Enunciado: Mostrar la cantidad de retweets para los tweets que no se hayan hecho en Argentina ni Brasil, pero sí tengan un lugar definido y sean en español.
 * Concepto: $ne null (campo presente y no nulo) y $nin (not in)
 */
declare const db: any;

db.tweets.find(
  {
    lang: "es",
    place: { $ne: null },                               // "tiene lugar definido": excluye null Y campos ausentes
    "place.country": { $nin: ["Argentina", "Brasil"] }, // ni Argentina ni Brasil
  },
  { _id: 0, "place.country": 1, "place.full_name": 1, retweet_count: 1 },
)
// No hace falta aggregate: es un filtro + proyección. Aggregate entra cuando hay que AGRUPAR o transformar.
