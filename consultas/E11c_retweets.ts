/**
 * Título: E11c - Los retweets heredan el contador
 * Enunciado: Ver, en los retweets con más retweet_count, de dónde sale ese número.
 * Concepto: el retweet_count de un retweet es el del tweet ORIGINAL (dato embebido y copiado)
 */
declare const db: any;

db.tweets.find(
  { retweeted_status: { $exists: true } },  // solo retweets
  {
    _id: 0,
    "user.screen_name": 1,                  // quién retuiteó
    retweet_count: 1,                       // el número que E11 promedia
    "retweeted_status.user.screen_name": 1, // autor del tweet original
    "retweeted_status.retweet_count": 1,    // retweets del ORIGINAL
  },
)
  .sort({ retweet_count: -1 })
  .limit(4)
