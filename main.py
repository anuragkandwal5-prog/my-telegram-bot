import os
import telebot
from telebot import types
import requests
from flask import Flask
import threading

# टोकन और API Key सुरक्षित रूप से Render से आएँगी
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

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
        bot.reply_to(message, "बाबू, इसके लिए मैं yt-dlp का सेटअप कर रही हूँ, बस अगला अपडेट इसी का होगा! 🚀")

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

# 🤖 AI Chat का असली कोड (Groq के साथ)
def ask_ai(message):
    bot.reply_to(message, "आपके सवाल का जवाब प्रोसेस कर रही हूँ बाबू... ⏳")
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}", 
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama3-8b-8192", 
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

def run_bot():
    bot.polling(non_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
