/**
 * Título: E8 - Top 10 por retweets, ascendente
 * Enunciado: Mostrar de los 10 tweets con más retweets, su usuario y la cantidad de retweets. Ordenar la salida de forma ascendente.
 * Concepto: el pipeline es una secuencia: el orden de las etapas importa
 */
declare const db: any;

db.tweets.aggregate([
  { $sort: { retweet_count: -1 } },  // 1. los más retuiteados primero
  { $limit: 10 },                    // 2. me quedo con el top 10
  {
    $project: {                      // 3. renombro y recorto campos
      _id: 0,
      usuario: "$user.screen_name",
      retweet_count: 1,
    },
  },
  { $sort: { retweet_count: 1 } },   // 4. recién ahora ordeno ascendente
])
// Si hiciéramos sort ascendente + limit 10 obtendríamos los 10 MENOS retuiteados.
