import time
import schedule
import requests
import feedparser
from deep_translator import GoogleTranslator

TELEGRAM_BOT_TOKEN = '8760352008:AAEAMs8aU3ZzgJrVNpFWLi-Tg_j2KCSbU9U'

SOURCES = {
    "Investing Live": "https://www.investing.com/rss/news_25.rss",
    "Forex Factory": "https://www.forexfactory.com/news/rss",
    "Metals Daily": "https://metalsdaily.com/rss"
}

sent_news = set()
sent_my_messages = set()
USERS_FILE = 'users.txt'
last_update_id = 0

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

# پشکنینی پەیامەکان و ناردنی بۆ گشت بەکارهێنەران
def check_telegram_updates():
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
                chat = message.get('chat', {})
                chat_id = chat.get('id')
                text = message.get('text', '') or message.get('caption', '')
                
                if chat and chat.get('type') == 'private' and text:
                    if text == '/start':
                        users = load_users()
                        if str(chat_id) not in users:
                            save_user(chat_id)
                            welcome_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                            welcome_payload = {
                                'chat_id': chat_id, 
                                'text': "سڵاو! بۆتەکە سەرکەوتووانە چالاک بوو و هەواڵەکانت بۆ دەنێرێت. 📊"
                            }
                            requests.post(welcome_url, json=welcome_payload, timeout=10)
                    else:
                        msg_id = message.get('message_id')
                        if msg_id not in sent_my_messages:
                            sent_my_messages.add(msg_id)
                            
                            formatted_msg = (
                                f"🚨 *MONEY HOTEL NEWS - هەواڵی خێرا*\n\n"
                                f"{text}\n\n"
                                f"----------------------------------\n"
                                f"بۆ شیکاری ڕۆژانەی بازاڕە دارایەکان تایبەت بە (ئاڵتون) ⬇️⬇️\n"
                                f"https://t.me/money_ffo"
                            )
                            send_telegram_message_to_all(formatted_msg)
                            print("Your message was successfully broadcasted!")
                            
    except Exception as e:
        print(f"Error checking updates: {e}")

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
                    sent_news.add(feed.entries[0].link)
        except Exception as e:
            print(f"Init error {source_name}: {e}")

def check_sources():
    print("Checking markets and updates...")
    check_telegram_updates()
    
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
                            f"🚨 *MONEY HOTEL NEWS - هەواڵی نوێ ({source_name})*\n\n"
                            f"📌 **{kurdish_title}**\n\n"
                            f"🔗 [تەواوی بابەتەکە بخوێنەوە]({link})\n\n"
                            f"----------------------------------\n"
                            f"بۆ شیکاری ڕۆژانەی بازاڕە دارایەکان تایبەت بە (ئاڵتون) ⬇️⬇️\n"
                            f"https://t.me/money_ffo"
                        )
                        
                        send_telegram_message_to_all(message)
                        print(f"New news sent from {source_name}!")
            else:
                print(f"Failed to fetch {source_name}, status code: {response.status_code}")
        except Exception as e:
            print(f"Error checking {source_name}: {e}")

initialize_rss()

schedule.every(1).minutes.do(check_sources)
print("Money Hotel News Bot is running smoothly...")

while True:
    schedule.run_pending()
    time.sleep(1)
