import telebot
import os
import uuid
from telebot import types, apihelper
import static_ffmpeg

# FFmpeg yo'llarini sozlash
static_ffmpeg.add_paths()

# Bot tokeningiz
TOKEN = "8765309750:AAH8UQApq7cGUYZr63DADSpVLh076lA2rLE"

apihelper.CONNECT_TIMEOUT = 120
apihelper.READ_TIMEOUT = 120
bot = telebot.TeleBot(TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🚀 <b>Tayyorman!</b>\n\nYouTube, Instagram yoki TikTok linkini yuboring:", parse_mode='html')

@bot.message_handler(func=lambda m: "http" in m.text)
def ask_format(message):
    user_data[message.chat.id] = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🎬 Video (MP4)", callback_data="mp4"),
        types.InlineKeyboardButton("🎵 Audio (MP3)", callback_data="mp3")
    )
    bot.reply_to(message, "Formatni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def download_logic(call):
    chat_id = call.message.chat.id
    url = user_data.get(chat_id)
    if not url: return

    status_msg = bot.send_message(chat_id, "⏳ Yuklanmoqda, iltimos kuting...")
    file_id = str(uuid.uuid4())
    file_path = f"/tmp/{file_id}"
    
    # YouTube bloklarini chetlab o'tish uchun qo'shimcha parametrlar
    ytdlp_opts = '--no-check-certificate --no-warnings --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"'

    try:
        if call.data == "mp4":
            output = f"{file_path}.mp4"
            os.system(f'yt-dlp {ytdlp_opts} -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best" -o "{output}" "{url}"')
            with open(output, 'rb') as v:
                bot.send_video(chat_id, v, caption="✅ @Yuklovchilb_bot orqali yuklandi")
        else:
            output = f"{file_path}.mp3"
            os.system(f'yt-dlp {ytdlp_opts} -x --audio-format mp3 -o "{output}" "{url}"')
            with open(output, 'rb') as a:
                bot.send_audio(chat_id, a, caption="✅ @Yuklovchilb_bot orqali yuklandi")
        
        if os.path.exists(output):
            os.remove(output)
    except Exception as e:
        bot.send_message(chat_id, "❌ Xatolik: YouTube bu ulanishni chekladi. Boshqa link ko'ring yoki birozdan so'ng urinib ko'ring.")
    
    bot.delete_message(chat_id, status_msg.message_id)

print("Bot ishlamoqda...")
bot.polling(none_stop=True)
