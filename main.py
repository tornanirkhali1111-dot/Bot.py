import logging
import httpx
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# লগিং সেটআপ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- কনফিগারেশন (আপনার টোকেন এখানে সরাসরি বসানো হয়েছে) ---
TOKEN = '8538714337:AAFC9kxVTvojWm-uTSS7df6gsI4wOeYINTI'
TERABOX_API = "https://terabox.pikaapis.workers.dev/?url="
TG_INFO_API = "https://telegram-info.rakibsarvar12.workers.dev/?name="

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
        "I am your **Professional Multi-Tool Bot**. 🚀\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📍 **Available Services:**\n"
        "📞 **Phone Info:** Send number with + (e.g. +880...)\n"
        "📦 **Terabox:** Send any Terabox link.\n"
        "👤 **TG User:** Send `@username` to search.\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🔹 *Developed by Tech Master*"
    )
    await update.message.reply_text(welcome_msg, parse_mode=ParseMode.MARKDOWN)

# --- মেইন মেসেজ প্রসেসর ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # ১. টেলিগ্রাম ইউজারনেম (@username)
    if text.startswith('@'):
        username = text.replace('@', '')
        await update.message.reply_chat_action("typing")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{TG_INFO_API}{username}", timeout=15)
                data = response.json()
                if data.get('status') or data.get('ok'):
                    res = data.get('result', data)
                    info = (
                        f"👤 **Telegram User Data**\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 **ID:** `{res.get('id')}`\n"
                        f"🏷️ **Name:** {res.get('first_name', 'N/A')}\n"
                        f"🔗 **Username:** @{res.get('username', username)}\n"
                        f"📝 **Bio:** {res.get('bio', 'N/A')}"
                    )
                    await update.message.reply_text(info, parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text("❌ User not found!")
            except:
                await update.message.reply_text("⚠️ API Error!")

    # ২. টেরাবক্স লিঙ্ক
    elif "terabox" in text:
        await update.message.reply_chat_action("typing")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{TERABOX_API}{text}", timeout=20)
                data = response.json()
                if data.get('url'):
                    dl_msg = (
                        f"📦 **Terabox Link Generated**\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📄 **File:** `{data.get('filename', 'Direct File')}`\n"
                        f"⚖️ **Size:** {data.get('size', 'N/A')}\n\n"
                        f"🚀 [Download Now]({data.get('url')})"
                    )
                    await update.message.reply_text(dl_msg, parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text("❌ Could not get link!")
            except:
                await update.message.reply_text("⚠️ API Offline!")

    # ৩. ফোন নম্বর (+ দিয়ে শুরু)
    elif text.startswith('+'):
        info = get_phone_info(text)
        if info:
            res_msg = (
                f"📱 **Phone Info Found**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🌍 **Country:** {info['country']}\n"
                f"📡 **Carrier:** {info['carrier']}\n"
                f"⏰ **Timezone:** {info['timezone']}\n"
                f"🔢 **Formatted:** `{info['format']}`"
            )
            await update.message.reply_text(res_msg, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("❌ Invalid Number!")

    else:
        await update.message.reply_text("❓ Send a Phone Number (+), Terabox Link, or @Username.")

if __name__ == '__main__':
    # অ্যাপ্লিকেশন তৈরি
    application = ApplicationBuilder().token(TOKEN).build()
    
    # হ্যান্ডলার যোগ করা
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Admin, Your Professional Bot is starting...")
    application.run_polling()
