import logging
from instaloader import Instaloader
from dotenv import set_key
from utils.file_utils import load_cookies, save_cookies

logger = logging.getLogger(__name__)

def login_with_username_password(username, password):
    """Login to Instagram using username and password, then save cookies to .env."""
    loader = Instaloader()
    try:
        logger.info(f"🔑 Attempting to login with username: {username}")
        loader.login(username, password)

        # Get cookies from the session
        cookies = loader.context._session.cookies.get_dict()
        logger.debug(f"🍪 Cookies retrieved: {cookies}")

        # Save cookies to .env
        save_cookies({
            "INSTAGRAM_SESSIONID": cookies.get("sessionid", ""),
            "INSTAGRAM_DS_USER_ID": cookies.get("ds_user_id", ""),
            "INSTAGRAM_CSRFTOKEN": cookies.get("csrftoken", ""),
            "INSTAGRAM_RUR": cookies.get("rur", ""),
            "INSTAGRAM_MID": cookies.get("mid", ""),
            "INSTAGRAM_USERNAME": username
        })
        logger.info("✅ Login successful! Cookies saved to .env.")
        return True
    except Exception as e:
        logger.error(f"❌ Login failed: {str(e)}", exc_info=True)
        return False

def initialize_loader_with_cookies():
    """Initialize Instaloader with cookies from .env."""
    cookies = load_cookies()
    if not all(cookies.values()):
        logger.error("❌ Cookies are missing or incomplete in .env.")
        raise ValueError("Cookies are missing or incomplete in .env.")

    loader = Instaloader()
    loader.context._session.cookies.update(cookies)
    loader.context.username = cookies["INSTAGRAM_USERNAME"]
    logger.info("🍪 Instaloader initialized with cookies.")
    return loader
