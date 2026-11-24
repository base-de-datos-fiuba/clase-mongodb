/**
 * Título: E12 - Lista de tweets por usuario
 * Enunciado: Por cada usuario obtener una lista de ids de tweets y el largo de la misma.
 * Concepto: $push arma un array dentro del grupo; $size lo mide
 */
declare const db: any;

db.tweets.aggregate([
  {
    $group: {
      _id: "$user_id",
      tweets: { $push: "$_id" },          // junta los _id de cada grupo en un array
    },
  },
  { $addFields: { n_tweets: { $size: "$tweets" } } }, // agrega un campo calculado sin perder los demás
  { $sort: { n_tweets: -1 } },            // (para que se vean primero los más activos)
])
