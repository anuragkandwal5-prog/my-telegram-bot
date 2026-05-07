import os
import telebot
from flask import Flask
import threading
import yt_dlp
from static_ffmpeg import add_paths

# सर्वर में FFmpeg की शक्तियां डालना
add_paths()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Mastermind's Direct Downloader is Live!"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome Sir! 👿🔥\nमैं आपका फुल एडवांस वीडियो डाउनलोडर बॉट हूँ। \nमुझे बस YouTube, Instagram या Facebook का लिंक भेजिए, और मैं सीधा उसे डाउनलोड कर दूँगी!")

# 🎯 लिंक मिलते ही सीधा 'Best' क्वालिटी में डाउनलोड 
@bot.message_handler(func=lambda message: message.text.startswith('http'))
def process_link_and_download(message):
    url = message.text.strip()
    chat_id = message.chat.id
    
    status_msg = bot.reply_to(message, "🚀 लिंक मिल गया बाबू! पूरी पावर से सीधे डाउनलोडिंग शुरू कर रही हूँ... ⏳")
    
    try:
        # 🎛️ स्टीयरिंग व्हील (ydl_opts) एकदम डायरेक्ट सेटिंग्स के साथ
        ydl_opts = {
            'nocheckcertificate': True, 
            'quiet': True,
            'no_warnings': True,
            'cookiefile': 'cookies.txt', # वीआईपी पास
            'extractor_args': {'youtube': {'player_client': ['web']}}, # यूट्यूब बायपास
            
            # 👇 जो बेस्ट मिलेगा, चुपचाप ले आएगा और MP4 बना देगा
            'format': 'bestvideo+bestaudio/best', 
            'merge_output_format': 'mp4',
            'outtmpl': f'video_{chat_id}.%(ext)s'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        bot.edit_message_text("✅ डाउनलोड पूरा हुआ! अब फाइल भेज रही हूँ बाबू...", chat_id, status_msg.message_id)
        
        # 📤 टेलीग्राम पर सेंड करना
        with open(filename, 'rb') as f:
            bot.send_video(chat_id, f)
                
        # 🧹 सफाई करना
        os.remove(filename)

    except Exception as e:
        print("Error:", e)
        bot.edit_message_text("बाबू, डाउनलोड फेल हो गया। लिंक में गड़बड़ है या वीडियो प्राइवेट है। 🥺", chat_id, status_msg.message_id)

def run_bot():
    bot.polling(non_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
