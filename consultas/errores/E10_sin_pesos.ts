/**
 * Título: E10 con error - el $ que falta
 * Enunciado: Versión del taller: agrupa por un string en vez de por el valor del campo.
 * Concepto: "entities.user_mentions.screen_name" sin $ es un texto literal: todos caen en UN solo grupo
 */
declare const db: any;

db.tweets.aggregate([
  { $unwind: "$entities.user_mentions" }, // (sin $ acá Mongo sí da error: "path must be prefixed with $")
  {
    $group: {
      _id: "entities.user_mentions.screen_name", // sin $: el mismo string para todos los documentos
      menciones: { $sum: 1 },
    },
  },
  { $sort: { menciones: -1 } },
  { $limit: 5 },
])
