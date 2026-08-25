import time
import feedparser
from deep_translator import GoogleTranslator
import requests

# زانیارییە ڕاستەقینەکانی بۆت و کەناڵەکەت
TOKEN = "8760352008:AAEAMs8aU3ZzgJrVNpFWLi-Tg_j2KCSbU9U"
CHANNEL_USERNAME = "@hawal_san"

# بەکارهێنانی RSS ی فەرمی FXStreet بۆ هێنانی هەواڵ بە خێرایی و بێ کێشە
RSS_URL = "https://www.fxstreet.com/rss"

def get_latest_news():
    try:
        feed = feedparser.parse(RSS_URL)
        if feed.entries:
            latest_entry = feed.entries[0]
            title = latest_entry.title
            return title
    except Exception as e:
        print(f"Error fetching RSS: {e}")
    return None

def translate_to_kurdish(text):
    try:
        translated = GoogleTranslator(source='auto', target='ku').translate(text)
        return translated
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
    print("Bot started successfully and monitoring FXStreet RSS...")
    last_sent_news = ""
    
    while True:
        english_news = get_latest_news()
        if english_news and english_news != last_sent_news:
            last_sent_news = english_news
            
            # وەرگێڕانی تایتڵی هەواڵەکە بۆ زمانی کوردی سۆرانی
            kurdish_title = translate_to_kurdish(english_news)
            
            # شێوازی نامەکە هەروەک داوات کردووە
            formatted_message = f"""🔴 هەواڵە ئابووریەکان و شیکاری ڕۆژانە
MONEY HOTEL news

{kurdish_title}

وە ئەمەش بنوسرێت بۆ داخڵ بونی گروپی تایبەت بە سیگناڵ و شیکاری پەیوەندیمان پێوە بکەن👇🏻
@anyon_boss"""

            send_to_telegram(formatted_message)
            print("New news translated and posted to channel successfully!")
            
        # چاوەڕێکردنی ٥ خولەک (٣٠٠ چرکە) بۆ پشکنینی هەواڵی نوێ
        time.sleep(300)
