import os
import requests
from telegram import Update, File
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Environment variables from Render dashboard
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
BUNNY_STORAGE_ZONE = os.environ["BUNNY_STORAGE_ZONE"]
BUNNY_API_KEY = os.environ["BUNNY_API_KEY"]
BUNNY_STORAGE_HOST = os.environ.get("BUNNY_STORAGE_HOST", "storage.bunnycdn.com")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    caption = update.message.caption or document.file_name

    # Clean and prepare custom path (with optional folder)
    custom_path = caption.strip().replace("..", "").lstrip("/")
    if "/" not in custom_path:
        custom_path = f"{custom_path}"

    # Download file from Telegram to temp
    file: File = await context.bot.get_file(document.file_id)
    temp_path = f"/tmp/{document.file_name}"
    await file.download_to_drive(temp_path)

    # Upload to Bunny CDN
    with open(temp_path, "rb") as f:
        headers = {
            "AccessKey": BUNNY_API_KEY
        }
        url = f"https://{BUNNY_STORAGE_HOST}/{BUNNY_STORAGE_ZONE}/{custom_path}"
        response = requests.put(url, headers=headers, data=f)

    os.remove(temp_path)

    if response.status_code == 201:
        await update.message.reply_text(f"✅ Uploaded as `{custom_path}` to Bunny CDN.")
    else:
        await update.message.reply_text(f"❌ Upload failed. Status code: {response.status_code}")


if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    print("📦 Bot is running...")
    app.run_polling()
