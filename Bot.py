import logging
import httpx
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# লগিং সেটআপ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- API কনফিগারেশন ---
TERABOX_API = "https://terabox.pikaapis.workers.dev/?url="
TG_INFO_API = "https://telegram-info.rakibsarvar12.workers.dev/?name="
TOKEN = '8538714337:AAFC9kxVTvojWm-uTSS7df6gsI4wOeYINTI'

# --- ফাংশন: ফোন নম্বর ডিটেইলস ---
def get_phone_info(number_text):
    try:
        parsed = phonenumbers.parse(number_text)
        if not phonenumbers.is_valid_number(parsed):
            return None
        return {
            "country": geocoder.description_for_number(parsed, "en"),
            "carrier": carrier.name_for_number(parsed, "en"),
            "timezone": ", ".join(timezone.time_zones_for_number(parsed)),
            "format": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        }
    except:
        return None

# --- হ্যান্ডলার: /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_msg = (
        f"✨ **Hello, {user_name}!** ✨\n\n"
        "I am an **Ultra Professional Multi-Tool Bot**. 🚀\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📍 **What can I do?**\n"
        "📞 **Phone Info:** Send any number with country code.\n"
        "📦 **Terabox:** Send any Terabox link to download.\n"
        "👤 **TG User:** Send `@username` to get info.\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🔹 *Developed by Tech Master*"
    )
    
    keyboard = [[InlineKeyboardButton("Developer 🛠️", url="https://t.me/your_username")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_msg, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

# --- মেইন মেসেজ প্রসেসর ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # ১. যদি টেলিগ্রাম ইউজারনেম হয় (@username)
    if text.startswith('@'):
        username = text.replace('@', '')
        await update.message.reply_chat_action("typing")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{TG_INFO_API}{username}")
                data = response.json()
                if data.get('ok'):
                    res = data['result']
                    info = (
                        f"👤 **Telegram User Data**\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 **ID:** `{res.get('id')}`\n"
                        f"🏷️ **Name:** {res.get('first_name')}\n"
                        f"🔗 **Username:** @{res.get('username')}\n"
                        f"🤖 **Is Bot:** {'Yes' if res.get('is_bot') else 'No'}\n"
                        f"📝 **Bio:** {res.get('bio', 'N/A')}"
                    )
                    await update.message.reply_text(info, parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text("❌ User not found in database!")
            except:
                await update.message.reply_text("⚠️ API Error on User Search!")

    # ২. যদি টেরাবক্স লিঙ্ক হয়
    elif "terabox" in text:
        await update.message.reply_chat_action("upload_document")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{TERABOX_API}{text}")
                data = response.json()
                if data.get('url'):
                    dl_msg = (
                        f"📦 **Terabox Download Link**\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📄 **File:** `{data.get('filename', 'Unknown')}`\n"
                        f"⚖️ **Size:** {data.get('size', 'N/A')}\n\n"
                        f"🚀 [Click Here to Download]({data.get('url')})"
                    )
                    await update.message.reply_text(dl_msg, parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text("❌ Failed to bypass Terabox link!")
            except:
                await update.message.reply_text("⚠️ Terabox API is currently offline!")

    # ৩. যদি ফোন নম্বর হয় (+ দিয়ে শুরু)
    elif text.startswith('+'):
        info = get_phone_info(text)
        if info:
            res_msg = (
                f"📱 **Phone Identity Verified**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🌍 **Country:** {info['country']}\n"
                f"📡 **Carrier:** {info['carrier']}\n"
                f"⏰ **Timezone:** {info['timezone']}\n"
                f"🔢 **Formatted:** `{info['format']}`"
            )
            await update.message.reply_text(res_msg, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("❌ Invalid Phone Number or Country Code missing!")

    else:
        await update.message.reply_text("❓ I don't understand. Send a Number, Terabox Link, or @Username.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Admin, Your Professional Bot is Live! 🚀")
    application.run_polling()
