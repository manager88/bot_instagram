import os
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



cancel_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("❌ انصراف و بازگشت به منو", callback_data="cancel")]
])


logger = logging.getLogger(__name__)

WAITING_POST_LINK = 1
WAITING_HIGHLIGHT_LINK = 2
WAITING_STORY_LINK = 3
WAITING_CHARGE_AMOUNT = 4
WAITING_REALS_LINK = 5

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

IDPAY_HEADER = {
    'Content-Type':'application/json',
    'accept': 'application/json',
    'one-api-token': settings.ONE_API_TOKEN,
    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_user = update.effective_user
    

    user, created = await get_or_create_user(tg_user)

    keyboard = [
        [InlineKeyboardButton("📥 دانلود پست اینستاگرام", callback_data="download_post")],
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
            await update.message.reply_text(f"✅ لینک دانلود:\n{download_url}")
            await update.message.reply_text("بازگشت به منو اصلی با \\start")
    except Exception as e:
        await update.message.reply_text("❌ خطا در دریافت پست. بعداً تلاش کنید."+str(e))
        await update.message.reply_text("بازگشت به منو اصلی با \n /start ")
        logger.error(e)

    return ConversationHandler.END


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


async def handle_highlight_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text
    await update.message.reply_text(f"✅ لینک هایلایت دریافت شد:\n{link}")
    return ConversationHandler.END


async def handle_story_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text
    await update.message.reply_text(f"✅ لینک استوری دریافت شد:\n{link}")
    return ConversationHandler.END


async def handle_charge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t_amount = update.message.text

    try:
        t_amount = int(t_amount)
    except ValueError:
        await update.message.reply_text("❌ لطفاً فقط عدد وارد کنید.")
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
        await update.message.reply_text("❌ خطا در ارتباط با زرین‌پال.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عملیات لغو شد.")
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start),CallbackQueryHandler(handle_button)],
    states={
        WAITING_POST_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_post_link),
            CallbackQueryHandler(handle_navigation, pattern="^(cancel)$")],
        WAITING_REALS_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reals_link),
            CallbackQueryHandler(handle_navigation, pattern="^(cancel)$")],
        WAITING_HIGHLIGHT_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_highlight_link),
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
    app = ApplicationBuilder().token(token).build()

    app.add_handler(conv_handler)

    app.add_handler(CallbackQueryHandler(handle_navigation, pattern="^(cancel)$"))

    logger.info("🤖 Bot started...")
    app.run_polling()




