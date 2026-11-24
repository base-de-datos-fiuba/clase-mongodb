/**
 * Título: E13 - Retweets de los 10 usuarios más activos
 * Enunciado: Hallar la máxima cantidad de retweets totales que tuvieron los 10 usuarios con más tweets.
 * Concepto: agrupar, cortar, y volver a operar sobre el resultado (el patrón de Pizzagram)
 */
declare const db: any;

db.tweets.aggregate([
  {
    $group: {
      _id: "$user_id",
      usuario: { $first: "$user.screen_name" },
      tweets: { $sum: 1 },                     // cuántos tweets tiene
      retweets: { $sum: "$retweet_count" },    // cuántos retweets suman entre todos
    },
  },
  { $sort: { tweets: -1 } },   // 1. los 10 usuarios con más tweets...
  { $limit: 10 },
  { $sort: { retweets: -1 } }, // 2. ...y de esos, el de más retweets totales
  { $limit: 1 },
])
// Otra lectura del enunciado: "el máximo retweet_count de un tweet" -> retweets: { $max: "$retweet_count" }
