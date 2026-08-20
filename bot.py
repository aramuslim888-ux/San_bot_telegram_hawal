import time
import schedule
import requests
import feedparser
from deep_translator import GoogleTranslator

TELEGRAM_BOT_TOKEN = '8760352008:AAEAMs8aU3ZzgJrVNpFWLi-Tg_j2KCSbU9U'

# لێرە یوزەرنێمی کەناڵەکەت دانراوە کە لە وێنەکاندا دیارە
CHANNEL_ID = '@hawal_san'

SOURCES = {
    "Investing Live": "https://www.investing.com/rss/news_25.rss",
    "Forex Factory": "https://www.forexfactory.com/news/rss"
}

sent_news = set()
USERS_FILE = 'users.txt'

def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()

def save_user(chat_id):
    users = load_users()
    if str(chat_id) not in users:
        with open(USERS_FILE, 'a') as f:
            f.write(f"{chat_id}\n")

def send_telegram_message_to_all(message):
    # ناردنی پەیام بۆ کەناڵەکەت
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHANNEL_ID, 'text': message, 'parse_mode': 'Markdown'}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram Error for channel: {e}")

    # ناردنی پەیام بۆ ئەو کەسانەی کە /startـیان کردووە (وەک کۆدەکەی خۆت)
    users = load_users()
    for chat_id in users:
        try:
            requests.post(url, json={'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}, timeout=10)
        except Exception as e:
            print(f"Telegram Error for {chat_id}: {e}")

def check_updates():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for result in data.get('result', []):
                message = result.get('message', {})
                chat_id = message.get('chat', {}).get('id')
                text = message.get('text', '')
                if chat_id and text == '/start':
                    save_user(chat_id)
    except Exception as e:
        print(f"Error checking updates: {e}")

def check_sources():
    print("Checking markets for live news...")
    check_updates()
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
                            f"🚨 *MONEY HOTEL News - هەواڵی نوێ ({source_name})*\n\n"
                            f"📌 **{kurdish_title}**\n\n"
                            f"🔗 [تەواوی بابەتەکە بخوێنەوە]({link})\n\n"
                            f"----------------------------------\n"
                            f"بۆ شیکاری ڕۆژانەی بازاڕە داراییەکان 📊\n"
                            f"https://t.me/money_ffo"
                        )
                        
                        send_telegram_message_to_all(message)
                        print(f"New news sent to channel and users from {source_name}!")
            else:
                print(f"Failed to fetch {source_name}, status code: {response.status_code}")
        except Exception as e:
            print(f"Error checking {source_name}: {e}")

schedule.every(1).minutes.do(check_sources)
print("Money Hotel News Pro Bot is running smoothly...")
check_sources()

while True:
    schedule.run_pending()
    time.sleep(1)
