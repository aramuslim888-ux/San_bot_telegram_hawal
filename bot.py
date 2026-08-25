from deep_translator import GoogleTranslator
import feedparser
import json
import requests
import time

TOKEN = "8760352008:AAEAMs8aU3ZzgJrVNpFWLi-Tg_j2KCSbU9U"
CHANNEL_ID = "@hawal_san"
RSS_URL = "https://www.fxstreet.com/rss"


def send_to_telegram(title, summary, link, image_url=None):
  url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
  message = f"🚨 **{title}**\n\n{summary}"
  keyboard = {
      "inline_keyboard": [[{"text": "Read More 👈", "url": link}]]
  }
  data = {
      "chat_id": CHANNEL_ID,
      "text": message,
      "parse_mode": "Markdown",
      "reply_markup": json.dumps(keyboard),
  }
  try:
    response = requests.post(url, data=data)
    print(f"Telegram response: {response.text}")
  except Exception as e:
    print(f"Error: {e}")


def main():
  print("Fxstreet Bot with fast checking is running...")
  sent_posts = set()

  # پشکنینی یەکەم دەستبەجێ کاتێک کار دەکات
  while True:
    try:
      feed = feedparser.parse(RSS_URL)
      for entry in feed.entries[:3]:
        if entry.link not in sent_posts:
          title = entry.title
          summary = entry.summary if "summary" in entry else ""

          try:
            title_ku = GoogleTranslator(
                source="auto", target="ku"
            ).translate(title)
            summary_ku = GoogleTranslator(
                source="auto", target="ku"
            ).translate(summary)
          except:
            title_ku = title
            summary_ku = summary

          send_to_telegram(title_ku, summary_ku, entry.link)
          sent_posts.add(entry.link)
          time.sleep(2)
    except Exception as e:
      print(f"Error in loop: {e}")

    # کەمکردنەوەی کاتی چاوەڕوانی بۆ ٣٠ چرکە تاوەکو خێرا هەواڵەکان بهێنێت
    time.sleep(30)


if __name__ == "__main__":
  main()
