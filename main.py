import os
import requests
from telegram import Update, File
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Bunny CDN configuration
BUNNY_STORAGE_ZONE = "your-storage-zone-name"
BUNNY_API_KEY = "your-storage-zone-api-key"
BUNNY_STORAGE_HOST = "storage.bunnycdn.com"

# Bot token from BotFather
TELEGRAM_BOT_TOKEN = "your-telegram-bot-token"

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    custom_name = update.message.caption or document.file_name  # Use caption as new filename if provided

    # Download the file from Telegram
    file: File = await context.bot.get_file(document.file_id)
    file_path = f"/tmp/{document.file_name}"
    await file.download_to_drive(file_path)

    # Upload to Bunny CDN
    with open(file_path, "rb") as f:
        headers = {
            "AccessKey": BUNNY_API_KEY
        }
        response = requests.put(
            f"https://{BUNNY_STORAGE_HOST}/{BUNNY_STORAGE_ZONE}/{custom_name}",
            headers=headers,
            data=f
        )

    os.remove(file_path)

    if response.status_code == 201:
        await update.message.reply_text(f"✅ File uploaded as `{custom_name}` to Bunny CDN.")
    else:
        await update.message.reply_text(f"❌ Upload failed with status code: {response.status_code}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.run_polling()
