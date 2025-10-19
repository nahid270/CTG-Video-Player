import os
import threading
from flask import Flask, Response, render_template_string, jsonify
from pyrogram import Client, filters

# --- Config ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
STREAM_BASE_URL = os.environ.get("STREAM_BASE_URL", "https://yourappname.onrender.com")

app = Flask(__name__)
bot = Client("StreamServer", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Temporary storage (later can be replaced with database)
VIDEO_STORAGE = {}

# --- Flask Routes ---

@app.route('/')
def home():
    return "<h2>🎬 Telegram Movie Stream Server is Running!</h2>"

@app.route('/stream/<file_id>')
def stream_video(file_id):
    if file_id not in VIDEO_STORAGE:
        return jsonify({"error": "Invalid or expired file ID"}), 404
    file_path = VIDEO_STORAGE[file_id]
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Movie Player</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ margin: 0; background-color: black; }}
            video {{ width: 100%; height: 100vh; }}
        </style>
    </head>
    <body>
        <video controls autoplay>
            <source src="{file_path}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
    </body>
    </html>
    """
    return html


# --- Telegram Bot ---

@bot.on_message(filters.video | filters.document)
async def upload_and_generate_link(client, message):
    file = message.video or message.document
    msg = await message.reply_text("📤 Uploading file and generating link...")
    
    # Download locally
    file_path = await client.download_media(file)
    
    # Store in memory (you can replace this with permanent storage)
    VIDEO_STORAGE[file.file_id] = file_path
    
    # Generate stream link
    stream_link = f"{STREAM_BASE_URL}/stream/{file.file_id}"
    await msg.edit_text(f"✅ **Stream Link Generated!**\n\n🔗 [Click to Watch]({stream_link})\n\nYou can embed this link anywhere.", disable_web_page_preview=True)


# --- Run Flask + Bot Together ---

def run_flask():
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run()
