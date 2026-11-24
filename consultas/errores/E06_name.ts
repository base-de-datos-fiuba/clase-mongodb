/**
 * Título: E6 con error - "name" en la raíz
 * Enunciado: Versión del taller: busca name en la raíz del documento.
 * Concepto: error silencioso: name vive dentro del subdocumento user
 */
declare const db: any;

db.tweets.find(
  { name: /Juan/ }, // debería ser "user.name"
  { _id: 0, name: 1, screen_name: 1 },
)
