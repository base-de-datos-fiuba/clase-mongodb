/**
 * Título: E9 - Los 10 hashtags más usados
 * Enunciado: Encontrar los 10 hashtags más usados.
 * Concepto: $unwind + $group + $sum: 1 (contar)
 */
declare const db: any;

db.tweets.aggregate([
  { $unwind: "$entities.hashtags" },  // 1. un documento por cada hashtag de cada tweet
  {
    $group: {
      _id: "$entities.hashtags.text", // 2. GROUP BY texto del hashtag
      cantidad: { $sum: 1 },          //    COUNT(*): suma 1 por documento
    },
  },
  { $sort: { cantidad: -1 } },        // 3. ORDER BY cantidad DESC
  { $limit: 10 },                     // 4. LIMIT 10
])
