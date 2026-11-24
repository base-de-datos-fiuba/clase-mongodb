/**
 * Título: E10 - Los 5 usuarios más mencionados
 * Enunciado: Encontrar los 5 usuarios más mencionados.
 * Concepto: $unwind de un array de objetos; las referencias a campos llevan $
 */
declare const db: any;

db.tweets.aggregate([
  { $unwind: "$entities.user_mentions" },           // un documento por cada @mención
  {
    $group: {
      _id: "$entities.user_mentions.screen_name",   // con $: el VALOR del campo. Sin $: un string literal
      menciones: { $sum: 1 },
    },
  },
  { $sort: { menciones: -1 } },
  { $limit: 5 },
])
