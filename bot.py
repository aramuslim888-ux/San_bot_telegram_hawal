import time
import requests
from bs4 import BeautifulSoup
from googletrans import Translator

# زانیارییە ڕاستەقینەکانی بۆت و کەناڵەکەت
TOKEN = "8760352008:AAEAMs8aU3ZzgJrVNpFWLi-Tg_j2KCSbU9U"
CHANNEL_USERNAME = "@hawal_san"

translator = Translator()

def get_latest_news():
    url = "https://www.fxstreet.com"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        news_item = soup.find('div', class_='qa-article-title') or soup.find('h3')
        if news_item:
            return news_item.get_text(strip=True)
    except Exception as e:
        print(f"Error fetching website: {e}")
    return None

def translate_to_kurdish(text):
    try:
        translation = translator.translate(text, dest='ku')
        return translation.text
    except Exception as e:
        print(f"Error in translation: {e}")
        return text

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_USERNAME,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Error sending to telegram: {e}")

if __name__ == "__main__":
    print("Bot started successfully and monitoring FXStreet...")
    last_sent_news = ""
    
    while True:
        english_news = get_latest_news()
        if english_news and english_news != last_sent_news:
            last_sent_news = english_news
            
            kurdish_title = translate_to_kurdish(english_news)
            
            formatted_message = f"""🔴 هەواڵە ئابووریەکان و شیکاری ڕۆژانە
MONEY HOTEL news

{kurdish_title}

وە ئەمەش بنوسرێت بۆ داخڵ بونی گروپی تایبەت بە سیگناڵ و شیکاری پەیوەندیمان پێوە بکەن👇🏻
@anyon_boss"""

            send_to_telegram(formatted_message)
            print("New news translated and posted to channel!")
            
        time.sleep(600)
