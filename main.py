import os
import telebot
from telebot import types
from flask import Flask
import threading
import yt_dlp
from static_ffmpeg import add_paths

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
    bot.reply_to(message, "Welcome Sir! 👿🔥\nमैं आपका डेडिकेटेड वीडियो डाउनलोडर बॉट हूँ। मुझे कोई भी वीडियो लिंक भेजिए!")

# 🎯 लाइव लिस्ट निकालने वाला फंक्शन
def fetch_and_send_qualities(chat_id, url, message_id):
    # 👇 यहाँ से Android वाली लाइन हमेशा के लिए हटा दी गई है
    ydl_opts = {
        'quiet': True, 
        'nocheckcertificate': True, 
        'cookiefile': 'cookies.txt'
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            resolutions = set()
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('height'):
                    resolutions.add(f.get('height'))
            
            sorted_res = sorted(list(resolutions), reverse=True)
            markup = types.InlineKeyboardMarkup(row_width=2)
            buttons = []
            
            for res in sorted_res:
                if res in [144, 240, 360, 480, 720, 1080, 1440, 2160]:
                    buttons.append(types.InlineKeyboardButton(f"🎬 {res}p", callback_data=f"dl_{res}"))
            
            if not buttons:
                buttons.append(types.InlineKeyboardButton("🎬 Best Video", callback_data="dl_best"))
                
            buttons.append(types.InlineKeyboardButton("🎵 Audio (MP3)", callback_data="dl_audio"))
            markup.add(*buttons)
            
            bot.edit_message_text("मास्टरमाइंड, इस वीडियो के लिए यह क्वालिटी लिस्ट मौजूद है। अपना फॉर्मेट चुनिए: 👇", chat_id, message_id, reply_markup=markup)
            
    except Exception as e:
        bot.edit_message_text(f"बाबू, क्वालिटी की लिस्ट निकालने में कोई गड़बड़ हो गई या लिंक प्राइवेट है। 🥺", chat_id, message_id)

@bot.message_handler(func=lambda message: message.text.startswith('http'))
def process_link_direct(message):
    url = message.text.strip()
    user_urls[message.chat.id] = url
    msg = bot.reply_to(message, "यूट्यूब के सर्वर से क्वालिटी की लिस्ट निकाल रही हूँ बाबू... ⏳")
    threading.Thread(target=fetch_and_send_qualities, args=(message.chat.id, url, msg.message_id)).start()

@bot.callback_query_handler(func=lambda call: call.data.startswith('dl_'))
def callback_download(call):
    chat_id = call.message.chat.id
    url = user_urls.get(chat_id)
    
    if not url:
        return bot.answer_callback_query(call.id, "लिंक गायब हो गया बाबू, फिर से भेजिए!")

    status_msg = bot.edit_message_text("🚀 पूरी पावर से डाउनलोडिंग शुरू हो रही है बाबू... ⏳", chat_id, call.message.message_id)
    res_str = call.data.split('_')[1]
    
    try:
        # 👇 यहाँ से भी Android वाली लाइन हटा दी गई है
        ydl_opts = {
            'nocheckcertificate': True, 
            'quiet': True,
            'no_warnings': True,
            'cookiefile': 'cookies.txt'
        }

        if res_str == 'audio':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
            ydl_opts['outtmpl'] = f'audio_{chat_id}.%(ext)s'
        elif res_str == 'best':
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
            ydl_opts['merge_output_format'] = 'mp4'
            ydl_opts['outtmpl'] = f'video_best_{chat_id}.%(ext)s'
        else:
            height = int(res_str)
            ydl_opts['format'] = f'bestvideo[height<={height}]+bestaudio/best'
            ydl_opts['merge_output_format'] = 'mp4'
            ydl_opts['outtmpl'] = f'video_{height}_{chat_id}.%(ext)s'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if res_str == "audio":
                filename = filename.rsplit('.', 1)[0] + '.mp3'

        bot.edit_message_text("✅ डाउनलोड पूरा हुआ! अब फाइल भेज रही हूँ...", chat_id, status_msg.message_id)
        
        with open(filename, 'rb') as file_data:
            if res_str == "audio":
                bot.send_audio(chat_id, file_data)
            else:
                bot.send_video(chat_id, file_data)
                
        os.remove(filename)
        bot.delete_message(chat_id, status_msg.message_id)

    except Exception as e:
        print("Error:", e) 
        bot.edit_message_text("बाबू, डाउनलोड करने में कोई दिक्कत आ गई। 🥺", chat_id, status_msg.message_id)

def run_bot():
    bot.polling(non_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
