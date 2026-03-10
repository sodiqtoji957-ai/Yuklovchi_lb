import telebot
import os
import uuid
from telebot import types, apihelper

# Bot tokeningiz
TOKEN = "8765309750:AAH8UQApq7cGUYZr63DADSpVLh076lA2rLE"

# Kutish vaqtini uzaytirish (MP3 xatosini tuzatish uchun)
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
    status_msg = bot.edit_message_text("⏳ Ishlanmoqda, iltimos kuting...", chat_id, call.message.message_id)
    
    file_id = str(uuid.uuid4())
    try:
        if call.data == "mp4":
            file_name = f"{file_id}.mp4"
            os.system(f'yt-dlp -f "best" -o "{file_name}" "{url}"')
            with open(file_name, 'rb') as v:
                bot.send_video(chat_id, v, caption="✅ @Yuklovchilb_bot", timeout=120)
        else:
            file_name = f"{file_id}.mp3"
            os.system(f'yt-dlp -x --audio-format mp3 -o "{file_name}" "{url}"')
            with open(file_name, 'rb') as a:
                bot.send_audio(chat_id, a, caption="✅ @Yuklovchilb_bot", timeout=120)
        
        os.remove(file_name)
    except Exception as e:
        bot.send_message(chat_id, f"❌ Xatolik: {e}")
    
    bot.delete_message(chat_id, status_msg.message_id)

print("Bot muvaffaqiyatli ishga tushdi...")
bot.polling(none_stop=True)
