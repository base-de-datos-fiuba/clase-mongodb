/**
 * Título: Pizzagram con error - sin $ en el group
 * Enunciado: La versión del taller (con { $unwind: {"$comentarios"} } corregido para que al menos corra).
 * Concepto: sin $, pizzeria e ip son strings fijos: un único grupo con TODOS los comentarios
 */
declare const db: any;

db.publicaciones.aggregate([
  { $unwind: "$comentarios" },
  {
    $group: {
      _id: { pizzeria: "pizzeria", ip: "ip" },   // debería ser "$pizzeria" y "$comentarios.ip"
      cantidad_comentarios: { $sum: 1 },
    },
  },
  { $match: { cantidad_comentarios: 10 } },      // el único grupo tiene miles -> no pasa nadie
  {
    $group: {
      _id: { ip: "ip" },                          // debería ser "$_id.ip"
      cantidad_pizzerias_ips: { $sum: 1 },
    },
  },
  { $sort: { cantidad_pizzerias_ips: -1 } },
  { $limit: 1 },
  {
    $project: {
      _id: 0,
      ip: "$_id",
      cantidad_pizzerias: "$cantidad_pizzerias_ips",
    },
  },
])
