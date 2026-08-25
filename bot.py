import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import json
import os
import time
import re
from urllib.parse import urljoin

# ==========================================
# TELEGRAM
# ==========================================

# لێرە Token ـی نوێی بۆتەکەت دابنێ
TOKEN = "PUT_YOUR_NEW_BOT_TOKEN_HERE"

# جەناڵەکەت
CHANNEL_ID = "@hawal_san"

# ==========================================
# FXSTREET
# ==========================================

FXSTREET_URL = "https://www.fxstreet.com/news"

CHECK_SECONDS = 60
MAX_NEWS = 5

SENT_FILE = "sent_news.json"


# ==========================================
# LOAD SENT NEWS
# ==========================================

def load_sent():

    if not os.path.exists(SENT_FILE):
        return set()

    try:
        with open(SENT_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))

    except:
        return set()


# ==========================================
# SAVE SENT NEWS
# ==========================================

def save_sent(sent):

    try:

        with open(SENT_FILE, "w", encoding="utf-8") as f:
            json.dump(
                list(sent)[-1000:],
                f,
                ensure_ascii=False,
                indent=2
            )

    except Exception as e:
        print("Save error:", e)


# ==========================================
# CLEAN TEXT
# ==========================================

def clean_text(text):

    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ==========================================
# TRANSLATE TO KURDISH
# ==========================================

def translate_kurdish(text):

    if not text:
        return ""

    try:

        result = GoogleTranslator(
            source="auto",
            target="ku"
        ).translate(text)

        return result if result else text

    except Exception as e:

        print("Translation error:", e)

        return text


# ==========================================
# GET FXSTREET NEWS
# ==========================================

def get_news():

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Linux; Android 10) "
            "AppleWebKit/537.36 "
            "Chrome/120.0 Mobile Safari/537.36"
        )
    }

    try:

        print("🔎 Checking FXStreet...")

        response = requests.get(
            FXSTREET_URL,
            headers=headers,
            timeout=20
        )

        print("FXStreet status:", response.status_code)

        if response.status_code != 200:
            print("❌ FXStreet page error")
            return []

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        news = []
        seen = set()

        # هەموو لینکەکانی هەواڵ دەدۆزینەوە
        for a in soup.find_all("a", href=True):

            href = a.get("href", "")
            title = clean_text(a.get_text(" ", strip=True))

            if not href.startswith("/news/"):
                continue

            if len(title) < 20:
                continue

            link = urljoin(
                "https://www.fxstreet.com",
                href
            )

            if link in seen:
                continue

            seen.add(link)

            news.append({
                "title": title,
                "link": link
            })

            if len(news) >= MAX_NEWS:
                break

        print("📰 News found:", len(news))

        return news

    except Exception as e:

        print("❌ FXStreet error:", e)

        return []


# ==========================================
# GET ARTICLE INFORMATION
# ==========================================

def get_article(link):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Linux; Android 10) "
            "AppleWebKit/537.36 "
            "Chrome/120.0 Mobile Safari/537.36"
        )
    }

    try:

        response = requests.get(
            link,
            headers=headers,
            timeout=20
        )

        if response.status_code != 200:
            return "", None

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        description = ""

        # OpenGraph description
        meta_description = soup.find(
            "meta",
            attrs={"property": "og:description"}
        )

        if meta_description:
            description = meta_description.get(
                "content",
                ""
            )

        # وێنە
        image_url = None

        meta_image = soup.find(
            "meta",
            attrs={"property": "og:image"}
        )

        if meta_image:
            image_url = meta_image.get(
                "content"
            )

        description = clean_text(description)

        return description, image_url

    except Exception as e:

        print("Article error:", e)

        return "", None


# ==========================================
# SEND TEXT
# ==========================================

def send_text(title, summary, link):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    message = (
        "🚨 <b>هەواڵی نوێ</b>\n\n"
        f"<b>{title}</b>\n\n"
        f"{summary}"
    )

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "📖 خوێندنەوەی تەواوی هەواڵ",
                    "url": link
                }
            ]
        ]
    }

    data = {
        "chat_id": CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
        "reply_markup": json.dumps(keyboard)
    }

    try:

        response = requests.post(
            url,
            data=data,
            timeout=20
        )

        result = response.json()

        print("Telegram:", result)

        return result.get("ok", False)

    except Exception as e:

        print("Telegram send error:", e)

        return False


# ==========================================
# SEND PHOTO
# ==========================================

def send_photo(title, summary, link, image_url):

    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    caption = (
        "🚨 <b>هەواڵی نوێ</b>\n\n"
        f"<b>{title}</b>\n\n"
        f"{summary}"
    )

    if len(caption) > 1000:
        caption = caption[:997] + "..."

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "📖 خوێندنەوەی تەواوی هەواڵ",
                    "url": link
                }
            ]
        ]
    }

    data = {
        "chat_id": CHANNEL_ID,
        "photo": image_url,
        "caption": caption,
        "parse_mode": "HTML",
        "reply_markup": json.dumps(keyboard)
    }

    try:

        response = requests.post(
            url,
            data=data,
            timeout=30
        )

        result = response.json()

        print("Telegram Photo:", result)

        return result.get("ok", False)

    except Exception as e:

        print("Photo error:", e)

        return False


# ==========================================
# MAIN
# ==========================================

def main():

    print("")
    print("====================================")
    print("       MONEY HOTEL NEWS BOT")
    print("====================================")
    print("Channel:", CHANNEL_ID)
    print("Source:", FXSTREET_URL)
    print("====================================")
    print("")

    sent = load_sent()

    while True:

        try:

            news = get_news()

            # لە کۆنەوە بۆ نوێ
            for item in reversed(news):

                link = item["link"]

                if link in sent:
                    continue

                original_title = item["title"]

                print("")
                print("📰 NEW NEWS:")
                print(original_title)

                # زانیاری زیاتر لە خودی article
                summary, image_url = get_article(link)

                # وەرگێڕانی ناونیشان
                title_ku = translate_kurdish(
                    original_title
                )

                # وەرگێڕانی کورتەی هەواڵ
                summary_ku = translate_kurdish(
                    summary
                )

                if not summary_ku:
                    summary_ku = (
                        "بۆ خوێندنەوەی وردەکارییەکانی "
                        "هەواڵەکە کرتە لەسەر دوگمەکە بکە."
                    )

                # کورتکردنەوە
                if len(summary_ku) > 1200:
                    summary_ku = (
                        summary_ku[:1200]
                        + "..."
                    )

                # ناردن بە وێنە ئەگەر هەبێت
                success = False

                if image_url:

                    success = send_photo(
                        title_ku,
                        summary_ku,
                        link,
                        image_url
                    )

                # ئەگەر وێنە کار نەکرد، تەنها text بنێرە
                if not success:

                    success = send_text(
                        title_ku,
                        summary_ku,
                        link
                    )

                if success:

                    sent.add(link)
                    save_sent(sent)

                    print("✅ هەواڵ نێردرا بۆ @hawal_san")

                else:

                    print("❌ نەتوانرا هەواڵ بنێردرێت")

                time.sleep(3)

        except Exception as e:

            print("❌ MAIN ERROR:", e)

        print("")
        print("⏳ Waiting 60 seconds...")
        print("")

        time.sleep(CHECK_SECONDS)


# ==========================================
# START
# ==========================================

if __name__ == "__main__":
    main()
