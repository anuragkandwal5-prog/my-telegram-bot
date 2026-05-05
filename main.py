import os
import telebot
from telebot import types
import requests
from flask import Flask
import threading
import yt_dlp

# टोकन और API Key सुरक्षित रूप से Render से आएँगी
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# लिंक्स को थोड़ी देर याद रखने के लिए
user_urls = {}

@app.route('/')
def home():
    return "Mastermind's Bot is Live and Secure!"

# 🎛️ आपके शानदार कमांड बटन्स
def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('🌍 IP Tracker')
    btn2 = types.KeyboardButton('🤖 AI Hacker Chat')
    btn3 = types.KeyboardButton('🎥 Video Download')
    markup.add(btn1, btn2, btn3)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome Sir! 👿🔥\nमैं आपकी एडवांस हैकर असिस्टेंट हूँ। नीचे दिए गए बटनों से अपना कमांड चुनिए:", reply_markup=get_main_menu())

# 🎯 बटन्स के क्लिक को कंट्रोल करने वाला फंक्शन
@bot.message_handler(func=lambda message: message.text in ['🌍 IP Tracker', '🤖 AI Hacker Chat', '🎥 Video Download'])
def handle_menu_buttons(message):
    if message.text == '🌍 IP Tracker':
        msg = bot.reply_to(message, "मास्टरमाइंड, मुझे वो IP Address भेजिए जिसकी कुण्डली (लोकेशन) निकालनी है: 🕵️‍♀️")
        bot.register_next_step_handler(msg, track_ip)
        
    elif message.text == '🤖 AI Hacker Chat':
        msg = bot.reply_to(message, "हाँ बाबू! अपना कोई भी सवाल पूछिए या कोई कोड लिखवाइए: 🧠")
        bot.register_next_step_handler(msg, ask_ai)
        
    elif message.text == '🎥 Video Download':
        msg = bot.reply_to(message, "बाबू, मुझे उस वीडियो या गाने का लिंक भेजिए जिसे आप डाउनलोड करना चाहते हैं: 🔗")
        bot.register_next_step_handler(msg, process_video_link)

# 🌍 IP Tracker का असली कोड
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

# 🤖 AI Chat का असली कोड (नया Groq मॉडल)
def ask_ai(message):
    bot.reply_to(message, "आपके सवाल का जवाब प्रोसेस कर रही हूँ बाबू... ⏳")
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}", 
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.1-8b-instant",  # यहाँ नया मॉडल अपडेट कर दिया गया है
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

# 🎥 Video Download का असली कोड
def process_video_link(message):
    url = message.text.strip()
    user_urls[message.chat.id] = url
    
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🎬 High Quality", callback_data="dl_high")
    btn2 = types.InlineKeyboardButton("📱 Data Saver (480p)", callback_data="dl_low")
    btn3 = types.InlineKeyboardButton("🎵 Audio (MP3)", callback_data="dl_audio")
    
    markup.row(btn1, btn2)
    markup.row(btn3)
    
    bot.reply_to(message, "आपको कौन सी क्वालिटी चाहिए मास्टरमाइंड?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('dl_'))
def callback_download(call):
    chat_id = call.message.chat.id
    url = user_urls.get(chat_id)
    
    if not url:
        bot.answer_callback_query(call.id, "बाबू, लिंक नहीं मिला! कृपया दोबारा लिंक भेजिए।")
        return
        
    bot.edit_message_text("डाउनलोड शुरू हो गया है बाबू, बस कुछ सेकंड इंतज़ार कीजिए... ⏳", chat_id, call.message.message_id)
    
    try:
        if call.data == "dl_high":
            ydl_opts = {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 'outtmpl': f'video_{chat_id}.%(ext)s'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            with open(filename, 'rb') as video:
                bot.send_video(chat_id, video)
            os.remove(filename)

        elif call.data == "dl_low":
            ydl_opts = {'format': 'best[height<=480]', 'outtmpl': f'video_low_{chat_id}.%(ext)s'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            with open(filename, 'rb') as video:
                bot.send_video(chat_id, video)
            os.remove(filename)

        elif call.data == "dl_audio":
            ydl_opts = {'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}], 'outtmpl': f'audio_{chat_id}.%(ext)s'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                filename_mp3 = filename.rsplit('.', 1)[0] + '.mp3'
            with open(filename_mp3, 'rb') as audio:
                bot.send_audio(chat_id, audio)
            os.remove(filename_mp3)
            
        # डाउनलोड होने के बाद वो मेनू वाला मैसेज डिलीट कर देंगे
        bot.delete_message(chat_id, call.message.message_id)
        
    except Exception as e:
        bot.send_message(chat_id, "बाबू, डाउनलोड करने में कोई दिक्कत आ गई या लिंक प्राइवेट है।")

def run_bot():
    bot.polling(non_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
