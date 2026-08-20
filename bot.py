import time
import schedule
import requests
import feedparser
from deep_translator import GoogleTranslator

TELEGRAM_BOT_TOKEN = '8760352008:AAEAMs8aU3ZzgJrVNpFWLi-Tg_j2KCSbU9U'

SOURCES = {
    "Investing Live": "https://www.investing.com/rss/news_25.rss",
    "Forex Factory": "https://www.forexfactory.com/news/rss"
}

sent_news = set()
USERS_FILE = 'users.txt'
last_update_id = 0  # بۆ ئەوەی تەنها پەیامی نوێ بخوێنرێتەوە و دووبارە نەبێتەوە

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
    users = load_users()
    for chat_id in users:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}
        try:
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            print(f"Telegram Error for {chat_id}: {e}")

# پشکنینی پەیامی /start بە شێوازێکی زیرەک کە دووبارە نەبێتەوە
def check_new_users():
    global last_update_id
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {'offset': last_update_id + 1, 'timeout': 1}
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for result in data.get('result', []):
                last_update_id = result.get('update_id', last_update_id)
                message = result.get('message', {})
                chat_id = message.get('chat', {}).get('id')
                text = message.get('text', '')
                
                if chat_id and text == '/start':
                    users = load_users()
                    if str(chat_id) not in users:
                        save_user(chat_id)
                    
                    # ناردنی پەیامی بەخێرهاتن تەنها بۆ ئەو کەسەی /start لێدەدات
                    welcome_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                    welcome_payload = {
                        'chat_id': chat_id, 
                        'text': "سڵاو! بۆتەکە سەرکەوتووانە چالاک بوو و هەواڵە ئابوورییەکانت بۆ دەنێرێت. 📊"
                    }
                    requests.post(welcome_url, json=welcome_payload, timeout=10)
    except Exception as e:
        print(f"Error checking updates: {e}")

# ڕێگری کردن لە ناردنی هەواڵە کۆنەکان لە یەکەم کاتی کارپێکردندا
def initialize_rss():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    for source_name, url in SOURCES.items():
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                if feed.entries:
                    # تەنها لینکە کۆنەکان دەخەینە ناو سەنت ئەوەوە بۆ ئەوەی پێشتر نەگەن
                    sent_news.add(feed.entries[0].link)
        except Exception as e:
            print(f"Init error {source_name}: {e}")

def check_sources():
    print("Checking markets for live news...")
    check_new_users()
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
                            f"🚨 *Aro B news - هەواڵی نوێ ({source_name})*\n\n"
                            f"📌 **{kurdish_title}**\n\n"
                            f"🔗 [تەواوی بابەتەکە بخوێنەوە]({link})\n\n"
                            f"----------------------------------\n"
                            f"هەواڵ و شیکاری ئابووری 📊\n"
                            f"Aro B news"
                        )
                        
                        send_telegram_message_to_all(message)
                        print(f"New news sent from {source_name}!")
            else:
                print(f"Failed to fetch {source_name}, status code: {response.status_code}")
        except Exception as e:
            print(f"Error checking {source_name}: {e}")

# جێبەجێکردنی سەرەتایی بۆ ئەوەی هەواڵی کۆن نەنێرێت
initialize_rss()

schedule.every(1).minutes.do(check_sources)
print("Aro B News Pro Bot is running smoothly...")

while True:
    schedule.run_pending()
    time.sleep(1)
