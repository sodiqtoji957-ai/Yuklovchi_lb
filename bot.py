import telebot
import os
import uuid
from telebot import types, apihelper
import static_ffmpeg  # Renderda ffmpeg ishlashi uchun shart

# FFmpeg-ni avtomatik sozlash
static_ffmpeg.add_paths()

# Bot tokeningiz
TOKEN = "8765309750:AAH8UQApq7cGUYZr63DADSpVLh076lA2rLE"

# Kutish vaqtini uzaytirish
apihelper.CONNECT_TIMEOUT = 120
apihelper.READ_TIMEOUT = 120
bot = telebot.TeleBot(TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🚀 <b>Tayyorman!</b>\n\nLink yuboring va formatni tanlang:", parse_mode='html')

@bot.message_handler(func=lambda m: "http" in m.text)
def ask_format(message):
    user_data[message.chat.id] = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🎬 Video (MP4)", callback_data="mp4"),
        types.InlineKeyboardButton("🎵 Audio (MP3)", callback_data="mp3")
    )
    bot.reply_to(message, "Qaysi formatda yuklaymiz?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def download_logic(call):
    chat_id = call.message.chat.id
    url = user_data.get(chat_id)
    
    if not url:
        bot.send_message(chat_id, "❌ Link topilmadi, iltimos qayta yuboring.")
        return

    status_msg = bot.edit_message_text("⏳ Ishlanmoqda, iltimos kuting...", chat_id, call.message.message_id)
    
    file_id = str(uuid.uuid4())
    # Renderda faqat /tmp papkasiga yozishga ruxsat bor
    file_path = f"/tmp/{file_id}"
    
    try:
        if call.data == "mp4":
            output_file = f"{file_path}.mp4"
            # yt-dlp ni to'g'ridan-to'g'ri chaqiramiz
            os.system(f'yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" -o "{output_file}" "{url}"')
            
            with open(output_file, 'rb') as v:
                bot.send_video(chat_id, v, caption="✅ @Yuklovchilb_bot", timeout=300)
        else:
            output_file = f"{file_path}.mp3"
            os.system(f'yt-dlp -x --audio-format mp3 -o "{output_file}" "{url}"')
            
            with open(output_file, 'rb') as a:
                bot.send_audio(chat_id, a, caption="✅ @Yuklovchilb_bot", timeout=300)
        
        # Faylni o'ch
