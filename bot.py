from deep_translator import GoogleTranslator
import feedparser
import json
import requests
import time

TOKEN = "8760352008:AAEAMs8aU3ZzgJrVNFWLi-Tg_j2KCSbU9U"
CHANNEL_ID = "@hawal_san"
RSS_URL = "https://www.fxstreet.com/rss"


def send_to_telegram(title, summary, link, image_url=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    message = f"🚨 **{title}**\n\n{summary}"

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "Read More 👈",
                    "url": link
                }
            ]
        ]
    }

    data = {
        "chat_id": CHANNEL_ID,
        "text": message,
        "parse_mode": "Markdown",
        "reply_markup": json.dumps(keyboard),
    }

    try:
        response = requests.post(
            url,
            data=data,
            timeout=20
        )

        print(f"Telegram response: {response.text}")

    except Exception as e:
        print(f"Error sending to Telegram: {e}")


def main():

    print("Fxstreet Bot is running...")

    sent_posts = set()

    while True:

        try:

            feed = feedparser.parse(RSS_URL)

            print(f"Found {len(feed.entries)} news items")

            for entry in feed.entries[:3]:

                if entry.link not in sent_posts:

                    title = entry.title

                    summary = (
                        entry.summary
                        if "summary" in entry
                        else ""
                    )

                    # وەرگێڕانی ناونیشان بۆ کوردی
                    try:

                        title_ku = GoogleTranslator(
                            source="auto",
                            target="ku"
                        ).translate(title)

                    except Exception as e:

                        print("Title translation error:", e)
                        title_ku = title


                    # وەرگێڕانی ناوەڕۆک بۆ کوردی
                    try:

                        summary_ku = GoogleTranslator(
                            source="auto",
                            target="ku"
                        ).translate(summary)

                    except Exception as e:

                        print("Summary translation error:", e)
                        summary_ku = summary


                    # ناردنی هەواڵ
                    send_to_telegram(
                        title_ku,
                        summary_ku,
                        entry.link
                    )

                    sent_posts.add(entry.link)

                    print("News sent:", title_ku)

                    time.sleep(2)

        except Exception as e:

            print(f"Error in loop: {e}")


        # پشکنینی نوێ هەر 30 چرکە
        print("Waiting 30 seconds...")

        time.sleep(30)


if __name__ == "__main__":
    main()
