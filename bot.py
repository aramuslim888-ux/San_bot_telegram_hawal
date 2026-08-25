import time
import schedule
import requests
import feedparser
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

TELEGRAM_BOT_TOKEN = '8760352008:AAEAMs8aU3ZzgJrVNpFWLi-Tg_j2KCSbU9U'
CHANNEL_ID = '@hawal_san'

# بەستەری نوێ و کارا کە ڕێگرییان لێ نەکراوە
SOURCES = {
    "FX Market News": "https://www.investing.com/rss/news_25.rss",
    "Forex Live": "https://www.forexlive.com/feed/news"
}

sent_news = set()

def send_telegram_message(chat_id, text, photo_url=None):
    if photo_url:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        payload = {'chat_id': chat_id, 'photo': photo_url, 'caption': text, 'parse_mode': 'Markdown'}
        try:
            res = requests.post(url, json=payload, timeout=15)
            if res.status_code == 200:
                return
        except:
            pass
            
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    try:
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"Telegram Error: {e}")

def check_sources():
    print("Checking markets for live news...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for source_name, url in SOURCES.items():
        try:
            response = requests.get(url, headers=headers, timeout=15)
            print(f"Status for {source_name}: {response.status_code}")
            
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                if feed.entries:
                    latest = feed.entries[0]
                    link = getattr(latest, 'link', '')
                    title = getattr(latest, 'title', '')
                    
                    if not link or not title:
                        continue
                        
                    image_url = None
                    if hasattr(latest, 'media_content') and latest.media_content:
                        image_url = latest.media_content[0].get('url')
                    elif hasattr(latest, 'enclosures') and latest.enclosures:
                        for enc in latest.enclosures:
                            if 'image' in enc.get('type', ''):
                                image_url = enc.get('href')
                                break
                    
                    summary_raw = getattr(latest, 'summary', '') or getattr(latest, 'description', '')
                    summary_text = BeautifulSoup(summary_raw, "html.parser").get_text() if summary_raw else ""
                    
                    if link not in sent_news:
                        sent_news.add(link)
                        
                        try:
                            kurdish_title = GoogleTranslator(source='auto', target='ckb').translate(title)
                        except:
                            kurdish_title = title
                            
                        kurdish_summary = ""
                        if summary_text:
                            try:
                                kurdish_summary = GoogleTranslator(source='auto', target='ckb').translate(summary_text[:800])
                            except:
                                kurdish_summary = summary_text
                        
                        message = (
                            f"🚨 *SAN FX - هەواڵی نوێ ({source_name})*\n\n"
                            f"📌 **{kurdish_title}**\n\n"
                        )
                        
                        if kurdish_summary:
                            message += f"📝 {kurdish_summary}\n\n"
                            
                        message += (
                            f"🔗 [تەواوی بابەتەکە بخوێنەوە]({link})\n\n"
                            f"----------------------------------\n"
                            f"هەواڵ و شیکاری ئابووری 📊\n"
                            f"SAN FX TRADING"
                        )
                        
                        send_telegram_message(CHANNEL_ID, message, image_url)
                        print(f"New news sent successfully from {source_name}!")
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
