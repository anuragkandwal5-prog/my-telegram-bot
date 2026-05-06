import os
import telebot
from telebot import types
from flask import Flask
import threading
import yt_dlp
from static_ffmpeg import add_paths # ⚙️ गियरबॉक्स

# सर्वर में FFmpeg की शक्तियां डालना
add_paths()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

user_urls = {}

@app.route('/')
def home():
    return "Mastermind's Video Downloader is Live!"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome Sir! 👿🔥\nमैं आपका डेडिकेटेड और सुपरफास्ट वीडियो डाउनलोडर बॉट हूँ। बस मुझे कोई भी वीडियो लिंक भेजिए!")

# 🎯 अब आप डायरेक्ट लिंक भेजेंगे तो भी बॉट काम करेगा
@bot.message_handler(func=lambda message: message.text.startswith('http'))
def process_link_direct(message):
    url = message.text.strip()
    user_urls[message.chat.id] = url
    
    # 🎛️ क्वालिटी चुनने के शानदार बटन्स
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1080 = types.InlineKeyboardButton("🎬 1080p (Full HD)", callback_data="dl_1080")
    btn720 = types.InlineKeyboardButton("📺 720p (HD)", callback_data="dl_720")
    btn480 = types.InlineKeyboardButton("📱 480p", callback_data="dl_480")
    btnAudio = types.InlineKeyboardButton("🎵 Audio (MP3)", callback_data="dl_audio")
    
    markup.add(btn1080, btn720, btn480, btnAudio)
    bot.reply_to(message, "मास्टरमाइंड, क्वालिटी चुनिए बाबू: 👇", reply_markup=markup)

# 🚀 स्पीडोमीटर (Progress Hook)
def my_hook(d, chat_id, message_id):
    if d['status'] == 'downloading':
        pass # लॉग्स साफ़ रखने के लिए हमने इसे शांत रखा है

@bot.callback_query_handler(func=lambda call: call.data.startswith('dl_'))
def callback_download(call):
    chat_id = call.message.chat.id
    url = user_urls.get(chat_id)
    
    if not url:
        return bot.answer_callback_query(call.id, "लिंक गायब हो गया बाबू, फिर से भेजिए!")

    status_msg = bot.edit_message_text("🚀 पूरी पावर से डाउनलोडिंग शुरू हो रही है बाबू... ⏳", chat_id, call.message.message_id)
    
    try:
        # 🎛️ स्टीयरिंग व्हील (ydl_opts) + VIP Pass (Cookies)
        ydl_opts = {
            'nocheckcertificate': True, 
            'quiet': True,
            'no_warnings': True,
            'cookiefile': 'cookies.txt', # 👈 हमारा वीआईपी पास
            'extractor_args': {'youtube': {'player_client': ['android']}}, 
            'progress_hooks': [lambda d: my_hook(d, chat_id, status_msg.message_id)] 
        }

        # 🎯 यूज़र की पसंद के हिसाब से क्वालिटी सेट करना
        if call.data == "dl_1080":
            ydl_opts['format'] = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]/best'
            ydl_opts['outtmpl'] = f'video_1080_{chat_id}.%(ext)s'
        elif call.data == "dl_720":
            ydl_opts['format'] = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]/best'
            ydl_opts['outtmpl'] = f'video_720_{chat_id}.%(ext)s'
        elif call.data == "dl_480":
            ydl_opts['format'] = 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]/best'
            ydl_opts['outtmpl'] = f'video_480_{chat_id}.%(ext)s'
        elif call.data == "dl_audio":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
            ydl_opts['outtmpl'] = f'audio_{chat_id}.%(ext)s'

        # 📥 डाउनलोडिंग प्रोसेस
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # ऑडियो के लिए फाइल का नाम .mp3 करना
            if call.data == "dl_audio":
                filename = filename.rsplit('.', 1)[0] + '.mp3'

        bot.edit_message_text("✅ डाउनलोड पूरा हुआ! अब फाइल भेज रही हूँ...", chat_id, status_msg.message_id)
        
        # 📤 टेलीग्राम पर सेंड करना
        with open(filename, 'rb') as file_data:
            if call.data == "dl_audio":
                bot.send_audio(chat_id, file_data)
            else:
                bot.send_video(chat_id, file_data)
                
        # 🧹 सफाई करना
        os.remove(filename)
        bot.delete_message(chat_id, status_msg.message_id)

    except Exception as e:
        print("Error:", e) 
        bot.edit_message_text("बाबू, यूट्यूब के सिक्योरिटी गार्ड ने रास्ता रोक दिया या लिंक में गड़बड़ है। 🥺", chat_id, status_msg.message_id)

def run_bot():
    bot.polling(non_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
