/**
 * Título: E14 - Tweets por usuario y por hora
 * Enunciado: Hallar para cada intervalo de una hora cuántos tweets realizó cada usuario.
 * Concepto: _id compuesto (GROUP BY de dos columnas) y operadores de fecha
 */
declare const db: any;

db.tweets.aggregate([
  {
    $group: {
      _id: {
        usuario: "$user.screen_name",
        hora: { $hour: "$created_at" }, // 21:50:10 -> 21 (todos los tweets son del mismo día)
      },
      tweets: { $sum: 1 },
    },
  },
  { $sort: { tweets: -1 } },
])
// Si hubiera varios días, $hour mezclaría las 21 h de todos. Para intervalos reales:
//   hora: { $dateTrunc: { date: "$created_at", unit: "hour" } }   // 2019-06-26T21:00:00Z
