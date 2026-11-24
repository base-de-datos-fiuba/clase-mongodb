/**
 * Título: E4 - Usuarios con tweets virales en español
 * Enunciado: Hallar los usuarios que tengan tweets con 200000 o más retweets y sean en idioma español.
 * Concepto: varias condiciones en el filtro = AND implícito; el idioma está en "lang"
 */
declare const db: any;

db.tweets.find(
  {
    retweet_count: { $gte: 200000 }, // 200000 o más
    lang: "es",                      // AND implícito: todas las claves del filtro se tienen que cumplir
  },
  { _id: 0, "user.screen_name": 1, retweet_count: 1 },
)
// Ojo: devuelve un documento por TWEET, así que un usuario puede repetirse.
// Para la lista de usuarios sin repetidos: db.tweets.distinct("user.screen_name", { ...mismo filtro... })
