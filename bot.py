from pyrogram import Client

# زانیاری ئەکاونتەکەت و بۆتەکەت
API_ID = 34131802
API_HASH = "b33e6e19212e48f0ba4d238bebb3a0d2"
TELEGRAM_BOT_TOKEN = '8760352008:AAEAMs8aU3ZzgJrVNpFWLi-Tg_j2KCSbU9U'

SOURCE_CHANNELS = ["hamai_haje01", "hawal_cxooo"]
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

# دروستکردنی کڵایتێک کە هەردووکیان پێکەوە ببەستێتەوە
app = Client("aro_news_session", api_id=API_ID, api_hash=API_HASH, bot_token=TELEGRAM_BOT_TOKEN)

@app.on_message()
async def forward_news(client, message):
    # پاشەکەوتکردنی ئەو کەسانەی بۆتەکەیان فۆڵۆ کردووە
    if message.chat.type.value == "private":
        save_user(message.chat.id)
        if message.text == "/start":
            await message.reply("سڵاو! بۆتەکە چالاک بوو و هەواڵەکانت بۆ دەنێرێت. 📊")
            return

    # پشکنین بۆ ئەوەی بزانین پەیامەکە لەو دوو چەناڵەیە یان نا
    if message.chat and message.chat.username in SOURCE_CHANNELS:
        users = load_users()
        text = message.text or message.caption or ""
        
        formatted_message = (
            f"🚨 *Aro B news - هەواڵی نوێ*\n\n"
            f"{text}\n\n"
            f"----------------------------------\n"
            f"هەواڵ و شیکاری ئابووری 📊\n"
            f"Aro B news"
        )
        
        for chat_id in users:
            try:
                if message.photo:
                    await client.send_photo(chat_id=int(chat_id), photo=message.photo.file_id, caption=formatted_message, parse_mode="markdown")
                elif message.video:
                    await client.send_video(chat_id=int(chat_id), video=message.video.file_id, caption=formatted_message, parse_mode="markdown")
                else:
                    await client.send_message(chat_id=int(chat_id), text=formatted_message, parse_mode="markdown")
            except Exception as e:
                print(f"Error: {e}")

print("Aro B News Userbot is running...")
app.run()
