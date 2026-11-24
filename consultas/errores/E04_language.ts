/**
 * Título: E4 con error - el campo "language"
 * Enunciado: Versión del taller: filtra por un campo language que no existe.
 * Concepto: error silencioso: en SQL sería "column does not exist"; en Mongo, simplemente nadie matchea
 */
declare const db: any;

db.tweets.find(
  {
    retweet_count: { $gte: 200000 },
    language: "es", // el campo se llama lang
  },
  { _id: 0, user_id: 1 },
)
