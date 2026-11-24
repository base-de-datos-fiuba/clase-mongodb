/**
 * Título: Pizzagram - El bot que operó en más pizzerías
 * Enunciado: Obtener la IP del bot (exactamente 10 comentarios para una misma pizzería) que haya operado en la mayor cantidad de pizzerías.
 * Concepto: $unwind + doble $group (el primero con _id compuesto) + $match como HAVING
 */
declare const db: any;

db.publicaciones.aggregate([
  { $unwind: "$comentarios" },                  // 1. un documento por comentario
  {
    $group: {                                   // 2. contar comentarios por (pizzería, ip)
      _id: { pizzeria: "$pizzeria", ip: "$comentarios.ip" },
      comentarios: { $sum: 1 },
    },
  },
  { $match: { comentarios: 10 } },              // 3. HAVING COUNT(*) = 10  ->  bots
  {
    $group: {                                   // 4. por cada ip bot, ¿en cuántas pizzerías operó?
      _id: "$_id.ip",
      cantidad_pizzerias: { $sum: 1 },
    },
  },
  { $sort: { cantidad_pizzerias: -1 } },        // 5. la que más
  { $limit: 1 },                                // 6.
  {
    $project: {                                 // 7. el formato pedido
      _id: 0,
      ip: "$_id",
      cantidad_pizzerias: "$cantidad_pizzerias",
    },
  },
])
