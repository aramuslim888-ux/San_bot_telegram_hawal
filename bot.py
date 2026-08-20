import time
import schedule
from pyrogram import Client, filters
from pyrogram.types import Message

# زانیاری بۆتەکەت
TELEGRAM_BOT_TOKEN = '8760352008:AAEAMs8aU3ZzgJrVNpFWLi-Tg_j2KCSbU9U'

# زانیاری ئەکاونتەکەت کە لە my.telegram.org وەرتگرتووە
API_ID = 34131802
API_HASH = "b33e6e19212e48f0ba4d238bebb3a0d2"

# دروستکردنی کڵایتەکی پیرۆگرام بۆ خوێندنەوەی چەناڵە گشتییەکان
app = Client("my_news_userbot", api_id=API_ID, api_hash=API_HASH, bot_token=TELEGRAM_BOT_TOKEN)

# لێرەدا هەردوو چەناڵەکەت داناوە بۆ ئەوەی بەیەکەوە چاودێر بکرێن
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

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    chat_id = message.chat.id
    save_user(chat_id)
    await message.reply("سڵاو! بۆتەکە سەرکەوتووانە چالاک بوو و هەواڵەکانت بۆ دەنێرێت. 📊")

# چاودێریکردنی هەردوو چەناڵەکە بۆ هەر پەیامێکی نوێ
@app.on_message(filters.chat(SOURCE_CHANNELS))
async def new_channel_post(client: Client, message: Message):
    users = load_users()
    
    # دەرهێنانی دەقی پەیامەکە یان کاپشنی وێنە/ڤیدیۆکە
    text = message.text or message.caption or ""
    
    # دروستکردنی ناوەڕۆکی نوێ بەبێ فۆروەرد و بە لۆگۆی خۆت
    formatted_message = (
        f"🚨 *Aro B news - هەواڵی نوێ*\n\n"
        f"{text}\n\n"
        f"----------------------------------\n"
        f"هەواڵ و شیکاری ئابووری 📊\n"
        f"Aro B news"
    )
    
    # ناردنەوەی بۆ هەموو ئەو کەسانەی بۆتەکەیان فۆڵۆ کردووە بێ نیشانەی فۆروەرد
    for chat_id in users:
        try:
            if message.photo:
                await client.send_photo(chat_id=int(chat_id), photo=message.photo.file_id, caption=formatted_message, parse_mode="markdown")
            elif message.video:
                await client.send_video(chat_id=int(chat_id), video=message.video.file_id, caption=formatted_message, parse_mode="markdown")
            else:
                await client.send_message(chat_id=int(chat_id), text=formatted_message, parse_mode="markdown")
        except Exception as e:
            print(f"Error sending to {chat_id}: {e}")

print("Aro B News Multi-Channel Userbot is running...")
app.run()
