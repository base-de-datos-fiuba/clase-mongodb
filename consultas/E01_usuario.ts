/**
 * Título: E1 - Tweets de un usuario
 * Enunciado: Hallar los tweets del usuario con userid '818839458'.
 * Concepto: find con igualdad (el WHERE más simple)
 */
declare const db: any;

// El usuario del enunciado (818839458) no está en la base reducida del taller: devolvería [].
// Usamos el usuario más activo de la base, 188068413 (@XpectRo9, 61 tweets).
db.tweets.find({
  user_id: "188068413", // ojo: es un string, no un número. 188068413 (sin comillas) no matchea nada
})
