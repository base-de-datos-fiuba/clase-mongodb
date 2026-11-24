/**
 * Título: Consulta libre
 * Enunciado: Escribí acá cualquier consulta y corréla con: python3 execute_query.py
 * Concepto: find(...) o aggregate([...]) sobre db.tweets o db.publicaciones (Pizzagram)
 */
declare const db: any;

db.tweets.find(
  { lang: "es", "place.country": "Argentina" },
  { _id: 0, "user.screen_name": 1, full_text: 1, retweet_count: 1 },
)
  .sort({ retweet_count: -1 })
  .limit(5)
