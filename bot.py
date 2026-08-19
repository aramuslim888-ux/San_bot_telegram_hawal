import time
import schedule
import requests
import feedparser
from deep_translator import GoogleTranslator

TELEGRAM_BOT_TOKEN = '8760352008:AAEAMs8aU3ZzgJrVNpFWLi-Tg_j2KCSbU9U'
TELEGRAM_CHAT_ID = '7216355415'

SOURCES = {
    "Investing Live": "https://www.investing.com/rss/news_25.rss",
    "Forex Factory": "https://www.forexfactory.com/news/rss"
}

sent_news = set()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram Error: {e}")

def check_sources():
    print("Checking markets for live news...")
    for source_name, url in SOURCES.items():
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                latest = feed.entries[0]
                link = latest.link
                title = latest.title
                
                if link not in sent_news:
                    sent_news.add(link)
                    
                    try:
                        kurdish_title = GoogleTranslator(source='auto', target='ku').translate(title)
                    except:
                        kurdish_title = title
                    
                    message = (
                        f"🚨 *SAN FX - هەواڵی نوێ ({source_name})*\n\n"
                        f"📌 **{kurdish_title}**\n\n"
                        f"🔗 [تەواوی بابەتەکە بخوێنەوە]({link})\n\n"
                        f"----------------------------------\n"
                        f"هەواڵ و شیکاری ئابووری 📊\n"
                        f"SAN FX TRADING"
                    )
                    
                    send_telegram_message(message)
                    print(f"New news sent from {source_name}!")
        except Exception as e:
            print(f"Error checking {source_name}: {e}")

schedule.every(1).minutes.do(check_sources)
print("San FX Pro Bot is running...")
check_sources()

while True:
    schedule.run_pending()
    time.sleep(1)
