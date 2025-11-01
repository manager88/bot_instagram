import os
import aiohttp
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters,CallbackQueryHandler,ConversationHandler
from django.conf import settings
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()
from .models import Transaction
from .utils import request_payment






############################ keywords ############################

cancel_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("❌ انصراف و بازگشت به منو", callback_data="cancel")]
])

############################ keywords ############################





############################ variables ############################

logger = logging.getLogger(__name__)

WAITING_POST_LINK = 1
WAITING_HIGHLIGHT_LINK = 2
WAITING_STORY_LINK = 3
WAITING_CHARGE_AMOUNT = 4
WAITING_REALS_LINK = 5
WAITING_AUDIO_LINK = 6

IDPAY_HEADER = {
    'Content-Type':'application/json',
    'accept': 'application/json',
    'one-api-token': settings.ONE_API_TOKEN,
    }
############################ variables ############################



############################ sync_to_async ############################

@sync_to_async
def get_or_create_user(tg_user):
    return User.objects.get_or_create(
        telegram_id=tg_user.id,
        username=tg_user.username,
        first_name=tg_user.full_name,
    )

@sync_to_async
def get_user_by_telrgramid(telegramId):
    return User.objects.get(telegram_id = telegramId)

@sync_to_async
def create_transaction(t_user, t_amount, t_type, t_status):
    if t_status:
        return Transaction.objects.create(user=t_user, amount=t_amount, type=t_type, status=t_status)
    else:
        return Transaction.objects.create(user=t_user, amount=t_amount, type=t_type)

############################ sync_to_async ############################











async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_user = update.effective_user
    

    user, created = await get_or_create_user(tg_user)

    keyboard = [
        [InlineKeyboardButton("📥 دانلود پست اینستاگرام", callback_data="download_post")],
        [InlineKeyboardButton("📥 دانلود صدای پست اینستاگرام", callback_data="download_audio")],
        [InlineKeyboardButton("📥 دانلود ریلز اینستاگرام", callback_data="download_reals")],
        [InlineKeyboardButton("📥 دانلود هایلایت اینستاگرام", callback_data="download_hilight")],
        [InlineKeyboardButton("📥 دانلود استوری اینستاگرام", callback_data="download_storeis")],
        [InlineKeyboardButton("💳 شارژ کیف پول", callback_data="charge")],
        [InlineKeyboardButton("💰 موجودی من", callback_data="balance")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! 👋 یکی از گزینه‌ها رو انتخاب کن:", reply_markup=markup)






async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "download_post":
        await query.message.reply_text("🔗 لینک پست اینستاگرام رو بفرست ، در صورت انصراف از ارسال جهت بازگشت به منو اصلی /start کلیک کنید.", reply_markup=cancel_keyboard)
        return WAITING_POST_LINK
    
    elif query.data == "download_audio":
        await query.message.reply_text("🔗 لینک پست یا ریلز اینستاگرام رو بفرست ، در صورت انصراف از ارسال جهت بازگشت به منو اصلی /start کلیک کنید", reply_markup=cancel_keyboard)
        return WAITING_AUDIO_LINK
     
    elif query.data == "download_reals":
        await query.message.reply_text("🔗 لینک ریلز اینستاگرام رو بفرست ، در صورت انصراف از ارسال جهت بازگشت به منو اصلی /start کلیک کنید", reply_markup=cancel_keyboard)
        return WAITING_REALS_LINK
       
    elif query.data == "download_hilight":
        await query.message.reply_text("🔗 لینک هایلایت اینستاگرام رو بفرست ، در صورت انصراف از ارسال جهت بازگشت به منو اصلی /start کلیک کنید", reply_markup=cancel_keyboard)
        return WAITING_HIGHLIGHT_LINK
    
    elif query.data == "download_storeis":
        await query.message.reply_text("🔗 لینک استوری اینستاگرام رو بفرست ، در صورت انصراف از ارسال جهت بازگشت به منو اصلی /start کلیک کنید", reply_markup=cancel_keyboard)
        return WAITING_STORY_LINK
    
    elif query.data == "charge":
        await query.message.reply_text("💳 مبلغ شارژ مورد نظر رو به عدد وارد کن ، در صورت انصراف از ارسال جهت بازگشت به منو اصلی /start کلیک کنید", reply_markup=cancel_keyboard)
        return WAITING_CHARGE_AMOUNT
    
    elif query.data == "balance":
        user = await get_user_by_telrgramid(update.effective_user.id)
        await query.message.reply_text(f"💰 موجودی شما: {user.balance} ریال")
        return ConversationHandler.END
    


async def handle_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        # بازگشت به منوی اصلی
        keyboard = [
            [InlineKeyboardButton("📥 دانلود پست اینستاگرام", callback_data="download_post")],
            [InlineKeyboardButton("📥 دانلود صدای پست اینستاگرام", callback_data="download_audio")],
            [InlineKeyboardButton("📥 دانلود ریلز اینستاگرام", callback_data="download_reals")],
            [InlineKeyboardButton("📥 دانلود هایلایت اینستاگرام", callback_data="download_hilight")],
            [InlineKeyboardButton("📥 دانلود استوری اینستاگرام", callback_data="download_storeis")],
            [InlineKeyboardButton("💳 شارژ کیف پول", callback_data="charge")],
            [InlineKeyboardButton("💰 موجودی من", callback_data="balance")],
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("🏠 بازگشت به منوی اصلی:", reply_markup=markup)
        return ConversationHandler.END

    






async def handle_post_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text
    x = link.split("/")
    await update.message.reply_text(f"✅ پست با لینک زیر ثبت شد:\n{link}")
    # اینجا می‌تونی کار دانلود پست از API رو انجام بدی
    """وقتی کاربر لینک پست اینستا می‌فرسته"""
    user = await get_user_by_telrgramid(update.effective_user.id)
    cost = 5000  # هزینه هر دانلود (ریال)
    if user.balance < cost:
        await update.message.reply_text(
            "موجودی کافی نیست ابتدا موجودی کیف پول خود را از منو اصلی افزایش دهید\n /start")
        return ConversationHandler.END

    # کم کردن از کیف پول
    user.balance -= cost
    #user.save()
    await sync_to_async(user.save)()

    #Transaction.objects.create(user=user, amount=cost, type="CHARGE", status="SUCCESS")
    await create_transaction(user, cost, t_type="CHARGE", t_status="SUCCESS")

    
    await update.message.reply_text("🔄 در حال دریافت پست از اینستاگرام...")

    # دانلود پست (مثلاً با API شخص ثالث)
    try:
        resp = requests.get(f"https://api.one-api.ir/instagram/v1/post/?shortcode={x[4]}",headers = IDPAY_HEADER,).json()
        if resp['status']==200:
            
            media=resp['result']['media'][0]
            download_url=media['url']
            await update.message.reply_text(f"✅ لینک دانلود:\n{download_url}", reply_markup=cancel_keyboard)
    except Exception as e:
        await update.message.reply_text("❌ خطا در دریافت پست. بعداً تلاش کنید."+str(e), reply_markup=cancel_keyboard)
        logger.error(e)



async def handle_audio_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text
    x = link.split("/")
    await update.message.reply_text(f"✅ پست با لینک زیر ثبت شد:\n{link}")
    # اینجا می‌تونی کار دانلود پست از API رو انجام بدی
    """وقتی کاربر لینک پست اینستا می‌فرسته"""
    user = await get_user_by_telrgramid(update.effective_user.id)
    cost = 5000  # هزینه هر دانلود (ریال)
    if user.balance < cost:
        await update.message.reply_text(
            "موجودی کافی نیست ابتدا موجودی کیف پول خود را از منو اصلی افزایش دهید\n /start")
        return ConversationHandler.END

    # کم کردن از کیف پول
    user.balance -= cost
    #user.save()
    await sync_to_async(user.save)()

    #Transaction.objects.create(user=user, amount=cost, type="CHARGE", status="SUCCESS")
    await create_transaction(user, cost, t_type="CHARGE", t_status="SUCCESS")

    
    await update.message.reply_text("🔄 در حال دریافت صدای پست از اینستاگرام...")

    # دانلود پست (مثلاً با API شخص ثالث)
    try:
        resp = requests.get(f"https://api.one-api.ir/instagram/v1/audio/?shortcode={x[4]}",headers = IDPAY_HEADER,).json()
        if resp['status']==200:
            
            media=resp['result']['metadata']['original_sound_info']['progressive_download_url']
            #download_url=media['url']
            await update.message.reply_text(f"✅ لینک دانلود:\n{media}", reply_markup=cancel_keyboard)
    except Exception as e:
        await update.message.reply_text("❌ خطا در دریافت پست. بعداً تلاش کنید."+str(e), reply_markup=cancel_keyboard)
        logger.error(e)
    


async def handle_reals_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text
    x = link.split("/")
    await update.message.reply_text(f"✅ ریلز با لینک زیر ثبت شد:\n{link}")
    # اینجا می‌تونی کار دانلود پست از API رو انجام بدی
    """وقتی کاربر لینک ریلز اینستا می‌فرسته"""
    user = await get_user_by_telrgramid(update.effective_user.id)
    cost = 5000  # هزینه هر دانلود (ریال)
    if user.balance < cost:
        await update.message.reply_text(
            "موجودی کافی نیست ابتدا موجودی کیف پول خود را از منو اصلی افزایش دهید\n /start"
        )
        return ConversationHandler.END

    # کم کردن از کیف پول
    user.balance -= cost
    #user.save()
    await sync_to_async(user.save)()

    await create_transaction(user, cost, t_type="CHARGE", t_status="SUCCESS")

    
    await update.message.reply_text("🔄 در حال دریافت ریلز از اینستاگرام...")

    # دانلود پست (مثلاً با API شخص ثالث)
    try:
        resp = requests.get(f"https://api.one-api.ir/instagram/v1/post/?shortcode={x[4]}",headers = IDPAY_HEADER,).json()
        if resp['status']==200:
            
            media=resp['result']['media'][0]
            download_url=media['url']
            await update.message.reply_text(f"✅ لینک دانلود:\n{download_url}")
    except Exception as e:
        await update.message.reply_text("❌ خطا در دریافت پست. بعداً تلاش کنید."+str(e))
        logger.error(e)

    return ConversationHandler.END


# async def handle_highlight_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text
    await update.message.delete()
    await update.message.reply_text(f"✅ نام کاربری دریافت شد:\n{link}")

    user = await get_user_by_telrgramid(update.effective_user.id)
    cost = 5000  # هزینه هر دانلود (ریال)
    if user.balance < cost:
        await update.message.reply_text(
            "موجودی کافی نیست ابتدا موجودی کیف پول خود را از منو اصلی افزایش دهید"
        )
        return ConversationHandler.END

    # کم کردن از کیف پول
    user.balance -= cost
    #user.save()
    await sync_to_async(user.save)()

    await create_transaction(user, cost, t_type="CHARGE", t_status="SUCCESS")

    
    await update.message.reply_text("🔄 در حال دریافت آی دی کاربر...")

    # دانلود پست (مثلاً با API شخص ثالث)
    try:
        resp = requests.get(f"https://api.one-api.ir/instagram/v1/user/?username={link}",headers = IDPAY_HEADER,).json()
        if resp['status']==200:  
           id = resp['result']['id']
           await update.message.edit_text(f"آی دی کاربر : {id}")
    except Exception as e:
        await update.message.reply_text("❌ خطا در دریافت پست. بعداً تلاش کنید."+str(e))
        logger.error(e)
        return ConversationHandler.END
    await update.message.edit_text("🔄 در حال دریافت لیست هایلایت ها...")
    try:
        resp = requests.get(f"https://api.one-api.ir/instagram/v1/user/highlights/?id={id}",headers = IDPAY_HEADER,).json()
        if resp['status']==200:  
           for item in resp['result']:
               hilight_id = item['id'].split(":")
               await update.message.reply_text(f"id : {hilight_id[1]}")
               await update.message.reply_text(f"موضوع  : {item['title']}")
               await update.message.reply_text("----------")

    except Exception as e:
        await update.message.reply_text("❌ خطا در دریافت پست. بعداً تلاش کنید."+str(e))
        logger.error(e)
        return ConversationHandler.END
    return ConversationHandler.END




async def handle_highlight_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text.replace("@", "").strip()
    await update.message.delete()
    await update.message.reply_text(f"✅ نام کاربری دریافت شد:\n{link}")

    user = await get_user_by_telrgramid(update.effective_user.id)
    cost = 5000  # هزینه هر دانلود (ریال)
    if user.balance < cost:
        await update.message.reply_text(
            "❌ موجودی کافی نیست. ابتدا کیف پول خود را از منوی اصلی افزایش دهید.\n/start"
        )
        return ConversationHandler.END

    # کم کردن از کیف پول
    user.balance -= cost
    await sync_to_async(user.save)()
    await create_transaction(user, cost, t_type="CHARGE", t_status="SUCCESS")

    await update.message.reply_text("🔄 در حال دریافت اطلاعات کاربر از اینستاگرام...")

    try:
        async with aiohttp.ClientSession() as session:
            # دریافت ID کاربر
            async with session.get(
                f"https://api.one-api.ir/instagram/v1/user/?username={link}",
                headers=IDPAY_HEADER,
            ) as resp:
                user_data = await resp.json()

            if user_data.get("status") != 200:
                await update.message.reply_text("❌ کاربر یافت نشد.")
                return ConversationHandler.END

            user_id = user_data["result"]["id"]
            await update.message.reply_text(f"آی دی کاربر : {user_id}")
            await update.message.reply_text("🔄 در حال دریافت لیست هایلایت ها...")

            # دریافت لیست هایلایت‌ها
            async with session.get(
                f"https://api.one-api.ir/instagram/v1/user/highlights/?id={user_id}",
                headers=IDPAY_HEADER,
            ) as resp2:
                highlights = await resp2.json()

            if highlights.get("status") != 200 or not highlights.get("result"):
                await update.message.reply_text("ℹ️ اکانت این کاربر خصوصی است و اجازه دانلود هایلایت ندارید.")
                return ConversationHandler.END

            keyboard = []
            try:

                for item in highlights["result"]:
                    highlight_id = item["id"].split(":")[1]
                    title = item.get("title", "بدون عنوان")
                    keyboard.append([
                        InlineKeyboardButton(f"🎯 {title}", callback_data=f"highlight_{highlight_id}")
                    ])

                markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    "📚 لیست هایلایت‌های کاربر:\nیکی را انتخاب کنید 👇",
                    reply_markup=markup
                )
            except Exception as e:
                logger.error(e)
                await update.message.reply_text(f"⚠️ هایلایت وجود ندارد: {e}")

                return ConversationHandler.END


            # ذخیره username در context برای استفاده بعدی
            context.user_data["insta_username"] = link

    except Exception as e:
        logger.error(e)
        await update.message.reply_text(f"⚠️ خطا در دریافت هایلایت‌ها: {e}")

    return ConversationHandler.END




async def handle_highlight_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not query.data.startswith("highlight_"):
        return

    highlight_id = query.data.split("_")[1]
    await query.message.reply_text("🔄 در حال دریافت محتوای هایلایت...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.one-api.ir/instagram/v1/highlight/?id={highlight_id}",
                headers=IDPAY_HEADER,
            ) as resp:
                data = await resp.json()

            if data.get("status") != 200 or not data.get("result"):
                await query.message.reply_text("❌ خطا در دریافت محتوای هایلایت.")
                return

            for media in data["result"]:
                url = media.get("url")
                mtype = media.get("type")
                if mtype == "video":
                    await query.message.reply_video(url)
                else:
                    await query.message.reply_photo(url)

        await query.message.reply_text("✅ همه محتوای هایلایت ارسال شدند.", reply_markup=cancel_keyboard)

    except Exception as e:
        logger.error(e)
        await query.message.reply_text(f"⚠️ خطا در دریافت محتوا: {e}")






async def handle_story_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text
    await update.message.reply_text(f"✅ نام کاربری دریافت شد:\n{link}")

    user = await get_user_by_telrgramid(update.effective_user.id)
    cost = 5000  # هزینه هر دانلود (ریال)
    if user.balance < cost:
        await update.message.reply_text(
            "موجودی کافی نیست ابتدا موجودی کیف پول خود را از منو اصلی افزایش دهید"
        )
        return ConversationHandler.END

    # کم کردن از کیف پول
    user.balance -= cost
    #user.save()
    await sync_to_async(user.save)()

    await create_transaction(user, cost, t_type="CHARGE", t_status="SUCCESS")

    
    await update.message.reply_text("🔄 در حال دریافت استوری از اینستاگرام...")

    # دانلود پست (مثلاً با API شخص ثالث)
    try:
        resp = requests.get(f"https://api.one-api.ir/instagram/v1/user/stories/?username={link}",headers = IDPAY_HEADER,).json()
        if resp.get("status") != 200 :
                await update.message.reply_text("ℹ️ اکانت این کاربر خصوصی است و اجازه دانلود هایلایت ندارید.",reply_markup=cancel_keyboard)
                return ConversationHandler.END
        if not resp.get("result"):
            await update.message.reply_text("ℹ️ استوری وجود ندارد.",reply_markup=cancel_keyboard)
            return ConversationHandler.END

        for item in resp['result']:
                url = item.get("url")
                mtype = item.get("type")
                if mtype == "video":
                    await update.message.reply_video(url)
                else:
                    await update.message.reply_photo(url)

        await update.message.reply_text("✅ همه محتوای هایلایت ارسال شدند.", reply_markup=cancel_keyboard)
    except Exception as e:
        await update.message.reply_text("❌ خطا در دریافت پست. بعداً تلاش کنید."+str(e))
        logger.error(e)

    return ConversationHandler.END



async def handle_charge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t_amount = update.message.text

    try:
        t_amount = int(t_amount)
    except ValueError:
        await update.message.reply_text("❌ لطفاً فقط عدد وارد کنید.", reply_markup=cancel_keyboard)
        return ConversationHandler.END  # خروج از تابع تا ادامه اجرا نشود

    await update.message.reply_text(f"💳 درخواست شارژ به مبلغ {str(t_amount)} ریال ثبت شد.")
    # اینجا می‌تونی پرداخت زرین‌پال رو فراخوانی کنی
    user = await get_user_by_telrgramid(update.effective_user.id)


    #tx = Transaction.objects.create(user=user, amount=amount, type="TOPUP")
    tx = await create_transaction(user, t_amount, t_type="TOPUP" , t_status=None)

    pay_url, authority = request_payment(
        amount=t_amount,
        description="شارژ کیف پول تلگرام",
        callback_url=settings.ZARINPAL_CALLBACK_URL,
        merchant_id=settings.ZARINPAL_MERCHANT_ID,
    )
    tx.authority = authority
    await sync_to_async(tx.save)()
    if pay_url:
        await update.message.reply_text(f"برای پرداخت، روی لینک زیر کلیک کنید:\n{pay_url}")
       
    else:
        await update.message.reply_text("❌ خطا در ارتباط با زرین‌پال.", reply_markup=cancel_keyboard)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عملیات لغو شد.")
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start),CallbackQueryHandler(handle_button)],
    states={
        WAITING_POST_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_post_link),
            CallbackQueryHandler(handle_navigation, pattern="^(cancel)$")],
        WAITING_AUDIO_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_audio_link),
            CallbackQueryHandler(handle_navigation, pattern="^(cancel)$")],
        WAITING_REALS_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reals_link),
            CallbackQueryHandler(handle_navigation, pattern="^(cancel)$")],
        WAITING_HIGHLIGHT_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_highlight_link),
            CallbackQueryHandler(handle_highlight_detail, pattern="^highlight_"),
            CallbackQueryHandler(handle_navigation, pattern="^(cancel)$")],
        WAITING_STORY_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_story_link),
            CallbackQueryHandler(handle_navigation, pattern="^(cancel)$")],
        WAITING_CHARGE_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_charge),
            CallbackQueryHandler(handle_navigation, pattern="^(cancel)$")],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_user=True, 
)



def run_bot():
    

    token = settings.TELEGRAM_TOKEN

    logging.info("🤖 Bot is initializing...")

    app = ApplicationBuilder().token(token).build()

    
    app.add_handler(CallbackQueryHandler(handle_highlight_detail, pattern="^highlight_"))
    app.add_handler(CallbackQueryHandler(handle_navigation, pattern="^(cancel)$"))

    app.add_handler(conv_handler)

    logging.info("✅ Bot is running...")
    app.run_polling(close_loop=False)  # جلوگیری از بستن event loop

