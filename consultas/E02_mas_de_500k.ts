/**
 * Título: E2 - Más de 500.000 retweets
 * Enunciado: Hallar aquellos tweets que tengan más de 500000 retweets.
 * Concepto: operadores de comparación ($gt, $gte, $lt, $lte, $ne)
 */
declare const db: any;

db.tweets.find(
  { retweet_count: { $gt: 500000 } }, // retweet_count > 500000
  { _id: 0, "user.screen_name": 1, retweet_count: 1, full_text: 1 }, // proyección: solo lo que nos interesa
)
