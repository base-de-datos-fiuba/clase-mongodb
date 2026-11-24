/**
 * Título: E7 - Top 10 por retweets (find)
 * Enunciado: Mostrar de los 10 tweets con más retweets, su usuario y la cantidad de retweets.
 * Concepto: el cursor: sort + limit
 */
declare const db: any;

db.tweets.find(
  {},                                                    // sin filtro: todos
  { _id: 0, "user.screen_name": 1, retweet_count: 1 },
)
  .sort({ retweet_count: -1 }) // -1 = descendente
  .limit(10)
