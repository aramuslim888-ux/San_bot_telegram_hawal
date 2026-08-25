from deep_translator import GoogleTranslator
import feedparser
import json
import requests
import time

# تۆکنی ڕاستەقینەی بۆتەکەت
TOKEN = "8760352008:AAEAMs8aU3ZzgJrVNpFWLi-Tg_j2KCSbU9U"
CHANNEL_ID = "@hawal_san"

# Linki RSS-i Fxstreet
RSS_URL = "https://www.fxstreet.com/rss"


def send_to_telegram_with_button(title, summary, link):
  url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

  # دروستکردنی شێوازی پەیامەکە وەک کەناڵە فەرمییەکان
  message = f"🚨 **{title}**\n\n{summary}"

  # دروستکردنی دوگمەی Read More (Inline Keyboard)
  keyboard = {
      "inline_keyboard": [[{"text": "Read More 🔗", "url": link}]]
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
  print("Fxstreet Bot is running...")

  # ناردنی پەیامی دڵنیایی
  url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
  requests.post(
      url,
      data={
          "chat_id": CHANNEL_ID,
          "text": (
              "🟢 **بۆتەکەی هەواڵی ئابووری Fxstreet بە شێوازی پۆستری فەرمی کەوتە"
              " کار!**"
          ),
          "parse_mode": "Markdown",
      },
  )

  sent_posts = set()
  while True:
    try:
      feed = feedparser.parse(RSS_URL)
      for entry in feed.entries[:5]:
        if entry.link not in sent_posts:
          title = entry.title
          summary = entry.summary if "summary" in entry else ""

          # وەرگێڕانی ووشەی بۆ کوردی
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

          # ناردنی هەواڵەکە بە دوگمەی Read More
          send_to_telegram_with_button(title_ku, summary_ku, entry.link)
          sent_posts.add(entry.link)
          time.sleep(5)
    except Exception as e:
      print(f"Error in loop: {e}")

    time.sleep(300)  # چاوەڕێی ٥ دەقە


if __name__ == "__main__":
  main()
