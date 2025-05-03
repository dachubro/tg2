async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    caption = update.message.caption or document.file_name

    # Sanitize caption to avoid invalid paths
    custom_path = caption.strip().replace("..", "").lstrip("/")
    if "/" not in custom_path:
        # If no folder specified, use filename directly
        custom_path = f"{custom_path}"

    # Download the file from Telegram
    file: File = await context.bot.get_file(document.file_id)
    temp_path = f"/tmp/{document.file_name}"
    await file.download_to_drive(temp_path)

    # Upload to Bunny CDN (supports folders)
    with open(temp_path, "rb") as f:
        headers = {
            "AccessKey": BUNNY_API_KEY
        }
        url = f"https://{BUNNY_STORAGE_HOST}/{BUNNY_STORAGE_ZONE}/{custom_path}"
        response = requests.put(url, headers=headers, data=f)

    os.remove(temp_path)

    if response.status_code == 201:
        await update.message.reply_text(f"✅ Uploaded as `{custom_path}`")
    else:
        await update.message.reply_text(f"❌ Upload failed: {response.status_code}")
