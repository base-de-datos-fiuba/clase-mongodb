/**
 * Título: E6 - Usuarios que se llaman Juan
 * Enunciado: Mostrar los screen name de aquellos usuarios que tengan "Juan" como parte de su nombre.
 * Concepto: regex y documentos embebidos (user.name)
 */
declare const db: any;

db.tweets.find(
  { "user.name": /Juan/ }, // el nombre vive DENTRO del subdocumento user. Con /Juan/i ignoraríamos mayúsculas
  { _id: 0, "user.name": 1, "user.screen_name": 1 },
)
