/**
 * Título: E11 - Promedio de retweets: Argentina vs. el resto
 * Enunciado: Hallar la cantidad de retweets promedio para los tweets que se hayan hecho desde Argentina y aquellos que no.
 * Concepto: el _id del $group puede ser una EXPRESIÓN calculada
 */
declare const db: any;

db.tweets.aggregate([
  {
    $group: {
      _id: {
        $cond: [                                    // un if/else: el grupo se llama según la condición
          { $eq: ["$place.country", "Argentina"] }, // ¿el tweet es de Argentina?
          "Argentina",                              // si sí
          "resto",                                  // si no: otro país, o sin place (da false también)
        ],
      },
      promedio_retweets: { $avg: "$retweet_count" },
      tweets: { $sum: 1 },
    },
  },
])
// Versión mínima: _id: { $eq: ["$place.country", "Argentina"] } -> dos grupos, true y false.
