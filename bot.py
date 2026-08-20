import time
import schedule
import requests
import feedparser
from deep_translator import GoogleTranslator

TELEGRAM_BOT_TOKEN = '8760352008:AAEAMs8aU3ZzgJrVNpFWLi-Tg_j2KCSbU9U'

# یوزەرنێمی کەناڵەکەت بۆ ئەوەی مەسجەکانی بۆ بنێرێت
CHANNEL_ID = '@hawal_san'

SOURCES = {
    "Investing Live": "https://www.investing.com/rss/news_25.rss",
    "Forex Factory": "https://www.forexfactory.com/news/rss"
}

sent_news = set()

def send_telegram_message_to_channel(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHANNEL_ID, 'text': message, 'parse_mode': 'Markdown'}
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"Telegram Error: {response.text}")
    except Exception as e:
        print(f"Telegram Error: {e}")

def check_sources():
    print("Checking markets for live news...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for source_name, url in SOURCES.items():
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                if feed.entries:
                    latest = feed.entries[0]
                    link = latest.link
                    title = latest.title
                    
                    if link not in sent_news:
                        sent_news.add(link)
                        
                        try:
                            kurdish_title = GoogleTranslator(source='auto', target='ckb').translate(title)
                        except:
                            kurdish_title = title
                        
                        message = (
                            f"🚨 *SAN FX - هەواڵی نوێ ({source_name})*\n\n"
                            f"📌 **{kurdish_title}**\n\n"
                            f"🔗 [تەواوی بابەتەکە بخوێنەوە]({link})\n\n"
                            f"----------------------------------\n"
                            f"هەواڵ و شیکاری ئابووری 📊\n"
                            f"SAN FX TRADING\n\n"
                            f"بۆ شیکاری ڕۆژانەی بازاڕە داراییەکان تایبەت بە (ئاڵتون) ⬇️⬇️\n"
                            f"https://t.me/money_ffo"
                        )
                        
                        send_telegram_message_to_channel(message)
                        print(f"New news sent to channel from {source_name}!")
            else:
                print(f"Failed to fetch {source_name}, status code: {response.status_code}")
        except Exception as e:
            print(f"Error checking {source_name}: {e}")

schedule.every(1).minutes.do(check_sources)
print("San FX Pro Bot is running...")
check_sources()

while True:
    schedule.run_pending()
    time.sleep(1)
