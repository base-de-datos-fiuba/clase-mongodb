/**
 * Título: E3 con error - el país en "geo"
 * Enunciado: Versión del taller: busca el país en el campo geo.
 * Concepto: error silencioso: geo existe, pero es un objeto GeoJSON {type, coordinates}, no un string
 */
declare const db: any;

db.tweets.find(
  { geo: { $in: ["Argentina", "Brasil"] } }, // ningún documento tiene geo == "Argentina" -> [] sin error
  { _id: 0, retweet_count: 1 },
)
