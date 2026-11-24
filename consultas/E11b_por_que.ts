/**
 * Título: E11b - ¿Por qué el resto promedia tanto más?
 * Enunciado: Mismo promedio de E11, pero separando tweets originales de retweets.
 * Concepto: _id compuesto con dos expresiones; $ifNull para preguntar si un campo existe
 */
declare const db: any;

db.tweets.aggregate([
  {
    $group: {
      _id: {
        grupo: {
          $cond: [{ $eq: ["$place.country", "Argentina"] }, "Argentina", "resto"],
        },
        tipo: { $cond: [{ $ifNull: ["$retweeted_status", false] }, "retweet", "original"] },
      },
      promedio_retweets: { $avg: "$retweet_count" },
      tweets: { $sum: 1 },
    },
  },
  { $sort: { "_id.grupo": 1, "_id.tipo": 1 } },
])
// $ifNull devuelve retweeted_status si existe (verdadero) o false si no está: un "¿tiene el campo?" dentro de una expresión.
