/**
 * Título: E3 - Retweets desde Argentina o Brasil
 * Enunciado: Mostrar la cantidad de retweets de los tweets que se hayan hecho desde Argentina o Brasil.
 * Concepto: $in (equivale a un $or sobre el mismo campo) y campos anidados con punto
 */
declare const db: any;

db.tweets.find(
  // El país NO está en "geo" (eso son coordenadas GeoJSON): está en place.country
  { "place.country": { $in: ["Argentina", "Brasil"] } },
  { _id: 0, "place.country": 1, retweet_count: 1 },
)
// Si quisiéramos la SUMA total de retweets, ya no alcanza con find: hace falta aggregate
//   db.tweets.aggregate([
//     { $match: { "place.country": { $in: ["Argentina", "Brasil"] } } },
//     { $group: { _id: "$place.country", retweets: { $sum: "$retweet_count" } } },
//   ])
