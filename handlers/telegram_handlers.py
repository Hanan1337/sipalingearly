import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils.instagram_utils import login_with_username_password

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    logger.info(f"🚀 /start command received from user: {update.message.from_user.username}")
    await update.message.reply_text(
        "📸 Send an Instagram profile URL to view:\n"
        "- HD Profile Picture\n"
        "- Latest Stories\n"
        "- Highlights\n"
        "- Profile Info\n\n"
        "Example URL: https://www.instagram.com/nasa/"
    )

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /login command with username and password."""
    logger.info(f"🔑 /login command received from user: {update.message.from_user.username}")
    args = context.args
    if len(args) != 2:
        logger.warning("❌ Invalid /login command format.")
        await update.message.reply_text("❌ Usage: /login <username> <password>")
        return

    username, password = args
    if login_with_username_password(username, password):
        await update.message.reply_text("✅ Login successful! Cookies saved to .env.")
    else:
        await update.message.reply_text("❌ Login failed. Please check your credentials.")
