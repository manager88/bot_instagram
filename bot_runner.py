import os
import time
import django
import logging
import traceback

# -------------------------------
# تنظیمات Django
# -------------------------------
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot_telegram_wallet.settings')
django.setup()

from bot.bot import run_bot  # مسیر ماژول ربات

# -------------------------------
# تنظیمات لاگر
# -------------------------------
LOG_FILE = "bot.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

# -------------------------------
# اجرای پایدار بات
# -------------------------------
if __name__ == "__main__":
    while True:
        try:
            logger.info("🚀 Starting Telegram bot...")
            run_bot()
        except Exception as e:
            logger.error("❌ Bot crashed: %s", e)
            traceback.print_exc()
            logger.info("♻️ Restarting bot in 10 seconds...")
            time.sleep(10)
