import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import phonenumbers
from phonenumbers import geocoder, carrier, timezone

# লগিং সেটআপ (ত্রুটি দেখার জন্য)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# /start কমান্ডের ফাংশন
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "স্বাগতম! 🤖\n\n"
        "যেকোনো ফোন নম্বর (কান্ট্রি কোড সহ) পাঠান, আমি তার তথ্য দেব।\n"
        "উদাহরণ: +88017XXXXXXXX"
    )

# নম্বর প্রসেস করার ফাংশন
async def number_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number_text = update.message.text
    
    try:
        # নম্বর পার্স করা
        parsed_number = phonenumbers.parse(number_text)
        
        # নম্বরটি সঠিক কিনা যাচাই করা
        if not phonenumbers.is_valid_number(parsed_number):
            await update.message.reply_text("❌ নম্বরটি সঠিক নয়। দয়া করে কান্ট্রি কোড সহ সঠিক নম্বর দিন।")
            return

        # তথ্য বের করা
        country = geocoder.description_for_number(parsed_number, "en")
        sim_carrier = carrier.name_for_number(parsed_number, "en")
        time_zones = timezone.time_zones_for_number(parsed_number)
        
        # ফরম্যাট করা উত্তর
        response = (
            f"📱 **Phone Number Info**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🌍 **Country:** {country}\n"
            f"📡 **Carrier:** {sim_carrier}\n"
            f"⏰ **Timezone:** {', '.join(time_zones)}\n"
            f"🔢 **Valid:** Yes"
        )
        
        await update.message.reply_text(response, parse_mode='Markdown')

    except phonenumbers.NumberParseException:
        await update.message.reply_text("❌ দয়া করে নম্বরের শুরুতে কান্ট্রি কোড দিন (যেমন: +880...)।")
    except Exception as e:
        await update.message.reply_text(f"একটি সমস্যা হয়েছে: {e}")

if __name__ == '__main__':
    # আপনার টেলিগ্রাম বটের টোকেন এখানে দিন
    TOKEN = 'YOUR_BOT_TOKEN_HERE'
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    # হ্যান্ডলার যোগ করা
    start_handler = CommandHandler('start', start)
    info_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), number_info)
    
    application.add_handler(start_handler)
    application.add_handler(info_handler)
    
    print("বট চালু হয়েছে...")
    application.run_polling()
