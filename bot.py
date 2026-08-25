from deep_translator import GoogleTranslator
import feedparser
import requests
import time

# Zanyariyakan
TOKEN = "Ghp_nbSqHpMZ6r1rviyNMfxI8Q7DmnG0eo1724RU"  # Tokne botakat
CHANNEL_ID = "@hawal_san"
# Linki RSS-i Fxstreet
RSS_URL = "https://www.fxstreet.com/rss"


def send_to_telegram(message):
  url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
  data = {"chat_id": CHANNEL_ID, "text": message}
  try:
    requests.post(url, data=data)
  except Exception as e:
    print(f"Error: {e}")


def main():
  print("Fxstreet Bot is running...")
  sent_posts = set()
  while True:
    try:
      feed = feedparser.parse(RSS_URL)
      for entry in feed.entries[:5]:
        if entry.link not in sent_posts:
          title = entry.title
          summary = entry.summary if "summary" in entry else ""

          # Wergirani wajai bo kurdi (agar pewist be)
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

          message = f"{title_ku}\n\n{summary_ku}\n\n{entry.link}"

          send_to_telegram(message)
          sent_posts.add(entry.link)
          time.sleep(5)
    except Exception as e:
      print(f"Error in loop: {e}")

    time.sleep(300)  # Chawary 5 deqe bo newe kirdnaway


if __name__ == "__main__":
  main()
