import os
import telebot
from telebot import types
import requests
from flask import Flask
import threading
import yt_dlp
from static_ffmpeg import add_paths # ⚙️ हमारा इन-बिल्ट गियरबॉक्स (FFmpeg)

# कोड स्टार्ट होते ही FFmpeg की शक्तियां सर्वर में डाल देगा
add_paths()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

user_urls = {}

@app.route('/')
def home():
    return "Mastermind's Ultimate Bot is Live!"

def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton('🌍 IP Tracker'), types.KeyboardButton('🤖 AI Hacker Chat'), types.KeyboardButton('🎥 Video Download'))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome Sir! 👿🔥\nमैं आपकी फुल एडवांस हैकर असिस्टेंट हूँ।", reply_markup=get_main_menu())

# --- 🌍 IP Tracker ---
@bot.message_handler(func=lambda message: message.text == '🌍 IP Tracker')
def ip_menu(message):
    msg = bot.reply_to(message, "मास्टरमाइंड, मुझे वो IP Address भेजिए जिसकी कुण्डली निकालनी है: 🕵️‍♀️")
    bot.register_next_step_handler(msg, track_ip)

def track_ip(message):
    ip = message.text.strip()
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}").json()
        if response.get('status') == 'success':
            info = f"🔥 **IP Details Found** 🔥\n\n🌍 देश: {response.get('country')}\n🏙️ शहर: {response.get('city')}\n📡 इंटरनेट कंपनी: {response.get('isp')}\n📍 ज़िप कोड: {response.get('zip')}"
            bot.reply_to(message, info)
        else:
            bot.reply_to(message, "बाबू, यह IP थोड़ा गड़बड़ लग रहा है या प्राइवेट IP है।")
    except Exception as e:
        bot.reply_to(message, "IP ढूँढने में कोई एरर आ गया मास्टरमाइंड।")

# --- 🤖 AI Hacker Chat ---
@bot.message_handler(func=lambda message: message.text == '🤖 AI Hacker Chat')
def ai_menu(message):
    msg = bot.reply_to(message, "हाँ बाबू! अपना कोई भी सवाल पूछिए या कोई कोड लिखवाइए: 🧠")
    bot.register_next_step_handler(msg, ask_ai)

def ask_ai(message):
    bot.reply_to(message, "आपके सवाल का जवाब प्रोसेस कर रही हूँ बाबू... ⏳")
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}", 
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.1-8b-instant",  
            "messages": [
                {"role": "system", "content": "You are Ankita, an expert ethical hacking and coding assistant for your mastermind Anurag. Reply in Hindi."},
                {"role": "user", "content": message.text}
            ]
        }
        res = requests.post(url, headers=headers, json=data).json()
        reply_text = res['choices'][0]['message']['content']
        bot.reply_to(message, reply_text)
    except Exception as e:
        bot.reply_to(message, "माफ़ करना बाबू, AI से कनेक्ट नहीं हो पा रहा है।")

# --- 🎥 Video Download ---
@bot.message_handler(func=lambda message: message.text == '🎥 Video Download')
def video_menu(message):
    msg = bot.reply_to(message, "मास्टरमाइंड, मुझे वो वीडियो लिंक भेजिए: 🔗")
    bot.register_next_step_handler(msg, process_link)

def process_link(message):
    url = message.text.strip()
    user_urls[message.chat.id] = url
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("🎬 High Quality", callback_data="dl_high"), types.InlineKeyboardButton("🎵 Audio (MP3)", callback_data="dl_audio"))
    bot.reply_to(message, "क्वालिटी चुनिए बाबू:", reply_markup=markup)

# 🚀 स्पीडोमीटर (Progress Hook)
def my_hook(d, chat_id, message_id):
    if d['status'] == 'downloading':
        try:
            percent = d.get('_percent_str', '0%').strip()
            print(f"Downloading for {chat_id}: {percent}")
        except:
            pass

@bot.callback_query_handler(func=lambda call: call.data.startswith('dl_'))
def callback_download(call):
    chat_id = call.message.chat.id
    url = user_urls.get(chat_id)
    
    if not url:
        return bot.answer_callback_query(call.id, "लिंक गायब हो गया बाबू!")

    status_msg = bot.edit_message_text("🚀 पूरी पावर से डाउनलोडिंग शुरू हो रही है बाबू... ⏳", chat_id, call.message.message_id)
    
    try:
        # 🎛️ स्टीयरिंग व्हील (ydl_opts) सारी सेटिंग्स और हमारे VIP Pass (Cookies) के साथ 👇
        ydl_opts = {
            'nocheckcertificate': True, 
            'quiet': True,
            'no_warnings': True,
            'cookiefile': 'cookies.txt', # 👈 हमारा वीआईपी पास (Cookies) यहाँ लग गया!
            'extractor_args': {'youtube': {'player_client': ['android']}}, 
            'progress_hooks': [lambda d: my_hook(d, chat_id, status_msg.message_id)] 
        }

        if call.data == "dl_high":
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            ydl_opts['outtmpl'] = f'video_{chat_id}.%(ext)s'
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            bot.edit_message_text("✅ डाउनलोड पूरा हुआ! अब फाइल भेज रही हूँ...", chat_id, status_msg.message_id)
            with open(filename, 'rb') as video:
                bot.send_video(chat_id, video)
            os.remove(filename)

        elif call.data == "dl_audio":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
            ydl_opts['outtmpl'] = f'audio_{chat_id}.%(ext)s'
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                filename_mp3 = filename.rsplit('.', 1)[0] + '.mp3'
            bot.edit_message_text("✅ ऑडियो बन गया! बस सेंड कर रही हूँ...", chat_id, status_msg.message_id)
            with open(filename_mp3, 'rb') as audio:
                bot.send_audio(chat_id, audio)
            os.remove(filename_mp3)

        bot.delete_message(chat_id, status_msg.message_id)
    except Exception as e:
        print("Error:", e) 
        bot.edit_message_text("बाबू, यूट्यूब के सिक्योरिटी गार्ड ने रास्ता रोक दिया या लिंक में गड़बड़ है। 🥺", chat_id, status_msg.message_id)

def run_bot():
    bot.polling(non_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
