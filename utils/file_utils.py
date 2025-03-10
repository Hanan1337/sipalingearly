import os
from dotenv import load_dotenv, set_key

def load_cookies():
    """Load Instagram cookies from .env."""
    load_dotenv()
    return {
        "INSTAGRAM_SESSIONID": os.getenv("INSTAGRAM_SESSIONID"),
        "INSTAGRAM_DS_USER_ID": os.getenv("INSTAGRAM_DS_USER_ID"),
        "INSTAGRAM_CSRFTOKEN": os.getenv("INSTAGRAM_CSRFTOKEN"),
        "INSTAGRAM_RUR": os.getenv("INSTAGRAM_RUR"),
        "INSTAGRAM_MID": os.getenv("INSTAGRAM_MID"),
        "INSTAGRAM_USERNAME": os.getenv("INSTAGRAM_USERNAME")
    }

def save_cookies(cookies):
    """Save Instagram cookies to .env."""
    for key, value in cookies.items():
        set_key(".env", key, value)

def secure_temp_dir():
    """Create a secure temporary directory."""
    temp_dir = os.path.join(os.getenv("SECURE_TEMP_DIR", "/tmp"), f"temp_{os.getpid()}")
    os.makedirs(temp_dir, mode=0o700, exist_ok=True)
    return temp_dir

def cleanup_temp_dir(directory):
    """Securely delete a temporary directory."""
    if os.path.exists(directory):
        shutil.rmtree(directory)
