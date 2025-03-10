import os
import logging
from telegram.ext import Application, CommandHandler
from handlers.telegram_handlers import start, login
from utils.logging_utils import setup_logging

logger = logging.getLogger(__name__)

def main():
    # Setup logging
    setup_logging()
    logger.info("🤖 Starting bot...")

    try:
        # Initialize the bot
        application = Application.builder().token(os.getenv("TOKEN_BOT")).build()

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("login", login))

        # Run the bot
        logger.info("✅ Bot started successfully")
        application.run_polling()
    except Exception as e:
        logger.error(f"❌ Bot failed to start: {str(e)}", exc_info=True)
    finally:
        logger.info("🛑 Bot stopped.")

if __name__ == "__main__":
    main()
