import requests
import aiohttp
import aiofiles
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Replace with your Telegram bot token
BOT_TOKEN = "7603077069:AAE_vQZJo-ZnAyFKicQ5sGWyrftnBRs71ZU"

# API Details
API_URL = "https://terabox-downloader-direct-download-link-generator2.p.rapidapi.com/url"
HEADERS = {
    "x-rapidapi-host": "terabox-downloader-direct-download-link-generator2.p.rapidapi.com",
    "x-rapidapi-key": "11dfba1a41mshcf2a3366f99eebbp1a10f5jsnf573ab35a4cc"
}

# Start Command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("👋 Welcome! Send me a Terabox URL, and I'll generate the direct download link for you.")

# Function to Download the Video
async def download_video(url, file_path):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=120) as response:  # Increased timeout
                if response.status == 200:
                    async with aiofiles.open(file_path, "wb") as f:
                        async for chunk in response.content.iter_chunked(1024):  # ✅ Fixed Chunked Download
                            await f.write(chunk)
                    return True
    except Exception as e:
        print(f"Download error: {e}")
    return False

# Handle Messages (User Input URL)
async def handle_message(update: Update, context: CallbackContext):
    user_url = update.message.text  # Get the URL sent by the user

    try:
        # Call the API
        params = {"url": user_url}
        response = requests.get(API_URL, headers=HEADERS, params=params, timeout=15)

        if response.status_code == 200:
            data = response.json()

            for item in data:
                file_name = item.get('file_name', 'video.mp4')
                file_size = item.get('size', 'Unknown')
                direct_link = item.get('direct_link', None)

                if not direct_link:
                    await update.message.reply_text("❌ Failed to get a direct link. Please try again.")
                    return

                message = (
                    f"✅ *Download Link Details:*\n"
                    f"📂 *File Name:* {file_name}\n"
                    f"📏 *File Size:* {file_size}\n"
                    f"🔗 *Direct Link:* [Click Here]({direct_link})"
                )

                await update.message.reply_text(message, parse_mode="Markdown", disable_web_page_preview=False)

                # Inform the user about downloading
                await update.message.reply_text("⏳ Downloading the video, please wait...")

                # Define file path
                file_path = f"./{file_name}"

                # Download the video asynchronously
                success = await download_video(direct_link, file_path)

                if success:
                    await update.message.reply_text("✅ Download complete. Uploading now...")

                    # Send the video to the user
                    await update.message.reply_video(video=open(file_path, "rb"))

                    # Delete file after sending
                    os.remove(file_path)
                else:
                    await update.message.reply_text("❌ Failed to download the video.")

        else:
            await update.message.reply_text(f"❌ API Error {response.status_code}: {response.text}")

    except Exception as e:
        await update.message.reply_text(f"⚠️ An error occurred: {str(e)}")

# Main Function to Start the Bot
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
