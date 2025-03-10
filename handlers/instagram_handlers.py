import logging
import os
import time
import pytz
import requests
from telegram import InputFile
from instaloader import Profile, QueryReturnedBadRequestException
from utils.instagram_utils import initialize_loader_with_cookies
from utils.file_utils import secure_temp_dir, cleanup_temp_dir

logger = logging.getLogger(__name__)

async def handle_profile_pic(query, username):
    """Handle downloading and sending the profile picture."""
    try:
        loader = initialize_loader_with_cookies()
        profile = Profile.from_username(loader.context, username)

        if profile.is_private and not profile.followed_by_viewer:
            await query.message.reply_text("🔒 Private profile - You are not following this account.")
            return

        # Get HD profile picture URL
        hd_url = profile.profile_pic_url.replace("/s150x150/", "/s1080x1080/")
        logger.info(f"📸 Downloading profile picture for @{username}")

        # Download the image
        response = requests.get(hd_url, stream=True)
        response.raise_for_status()

        # Save temporarily
        temp_file = f"temp_{username}_{int(time.time())}.jpg"
        with open(temp_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Send as a document
        await query.message.reply_document(
            document=open(temp_file, "rb"),
            filename=f"{username}_profile.jpg",
            caption=f"📸 Profile Picture of @{username}"
        )
        logger.info(f"✅ Profile picture sent for @{username}")

    except Exception as e:
        logger.error(f"❌ Failed to handle profile picture: {str(e)}", exc_info=True)
        await query.message.reply_text("⚠️ Failed to download profile picture.")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

async def handle_stories(query, username):
    """Handle downloading and sending Instagram stories."""
    temp_dir = None
    try:
        loader = initialize_loader_with_cookies()
        profile = Profile.from_username(loader.context, username)

        if profile.is_private and not profile.followed_by_viewer:
            await query.message.reply_text("🔒 Private profile - You are not following this account.")
            return

        # Get stories
        stories = []
        try:
            for story in loader.get_stories([profile.userid]):
                stories.extend(story.get_items())
        except QueryReturnedBadRequestException:
            await query.message.reply_text("🔒 Private profile - Bot cannot access stories.")
            return

        if not stories:
            await query.message.reply_text("📭 No stories available.")
            return

        # Sort stories by date (oldest first)
        stories.sort(key=lambda x: x.date_utc)

        # Set time zone (e.g., Asia/Jakarta for WIB)
        time_zone = pytz.timezone("Asia/Jakarta")

        # Create temporary directory
        temp_dir = secure_temp_dir()
        logger.info(f"🔄 Processing {len(stories)} stories for @{username}")

        sent_count = 0
        for story_item in stories:
            try:
                # Download story item
                loader.download_storyitem(story_item, temp_dir)
                time.sleep(3)

                # Find the downloaded file
                valid_extensions = ('.jpg', '.jpeg', '.png', '.mp4', '.mov')
                media_files = [
                    f for f in os.listdir(temp_dir)
                    if f.lower().endswith(valid_extensions)
                ]

                if not media_files:
                    logger.warning("No valid media files found.")
                    continue

                # Get the latest file
                latest_file = max(media_files, key=lambda f: os.path.getmtime(os.path.join(temp_dir, f)))

                # Check file size
                file_size = os.path.getsize(os.path.join(temp_dir, latest_file))
                if file_size > 50 * 1024 * 1024:  # 50MB limit
                    await query.message.reply_text("⚠️ File exceeds 50MB limit.")
                    os.remove(os.path.join(temp_dir, latest_file))
                    continue

                # Convert UTC time to local time
                local_time = story_item.date_utc.replace(tzinfo=pytz.utc).astimezone(time_zone)
                time_format = "%d-%m-%Y %H:%M"

                # Send the file
                with open(os.path.join(temp_dir, latest_file), "rb") as f:
                    if story_item.is_video:
                        await query.message.reply_video(
                            video=f,
                            caption=f"📹 {local_time.strftime(time_format)}",
                            read_timeout=60,
                            write_timeout=60
                        )
                    else:
                        await query.message.reply_photo(
                            photo=f,
                            caption=f"📸 {local_time.strftime(time_format)}",
                            read_timeout=60
                        )
                    sent_count += 1
                    logger.info(f"✅ Sent story item: {latest_file}")

                time.sleep(2)

            except Exception as e:
                logger.error(f"❌ Failed to process story item: {str(e)}", exc_info=True)
                continue

        await query.message.reply_text(f"📤 Total {sent_count} stories sent successfully.")

    except Exception as e:
        logger.error(f"❌ Failed to handle stories: {str(e)}", exc_info=True)
        await query.message.reply_text("⚠️ Failed to download stories.")
    finally:
        if temp_dir and os.path.exists(temp_dir):
            cleanup_temp_dir(temp_dir)

async def handle_highlights(query, username, page=0):
    """Handle downloading and sending Instagram highlights."""
    try:
        loader = initialize_loader_with_cookies()
        profile = Profile.from_username(loader.context, username)
        highlights = list(loader.get_highlights(user=profile))

        if not highlights:
            await query.message.reply_text("🌟 No highlights available.")
            return

        # Pagination logic
        items_per_page = 10
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        current_highlights = highlights[start_idx:end_idx]

        # Create inline keyboard for highlights
        keyboard = []
        for highlight in current_highlights:
            title = highlight.title[:15] + "..." if len(highlight.title) > 15 else highlight.title
            keyboard.append([
                InlineKeyboardButton(
                    f"🌟 {title}",
                    callback_data=f"highlight_{highlight.unique_id}"
                )
            ])

        # Add navigation buttons
        navigation_buttons = []
        if page > 0:
            navigation_buttons.append(
                InlineKeyboardButton("⏪ Back", callback_data=f"highlights_prev_{page - 1}")
            )
        if len(highlights) > end_idx:
            navigation_buttons.append(
                InlineKeyboardButton("⏩ Next", callback_data=f"highlights_next_{page + 1}")
            )

        if navigation_buttons:
            keyboard.append(navigation_buttons)

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            f"Select a highlight for @{username} (Page {page + 1}):",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"❌ Failed to handle highlights: {str(e)}", exc_info=True)
        await query.message.reply_text("⚠️ Failed to fetch highlights.")

async def handle_profile_info(query, username):
    """Handle sending Instagram profile information."""
    try:
        loader = initialize_loader_with_cookies()
        profile = Profile.from_username(loader.context, username)

        info_text = (
            f"📊 Profile Info for @{username}:\n"
            f"👤 Name: {profile.full_name}\n"
            f"📝 Bio: {profile.biography}\n"
            f"✅ Verified: {'Yes' if profile.is_verified else 'No'}\n"
            f"🏢 Business: {'Yes' if profile.is_business_account else 'No'}\n"
            f"🔗 Followers: {profile.followers:,}\n"
            f"👀 Following: {profile.followees:,}\n"
            f"📌 Posts: {profile.mediacount:,}"
        )

        await query.message.reply_text(info_text)
        logger.info(f"✅ Profile info sent for @{username}")

    except Exception as e:
        logger.error(f"❌ Failed to handle profile info: {str(e)}", exc_info=True)
        await query.message.reply_text("⚠️ Failed to fetch profile info.")
