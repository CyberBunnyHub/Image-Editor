from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
import os

# Flask Web App for Hosting
app = Flask(__name__)

@app.route("/")
def home():
    return "Hello from Flask Auto Filter Bot!"

# Bot Config
API_ID = int(os.getenv("API_ID", "14853951"))
API_HASH = os.getenv("API_HASH", "0a33bc287078d4dace12aaecc8e73545")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7845318227:AAFIWjneKzVu_MmAsNDkD3B6NvXzlbMdCgU")
FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL", "-1002614983879")  # Channel ID (not invite link)

bot = Client("autofilter-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    user = message.from_user

    # Force subscription
    try:
        await client.get_chat_member(FORCE_SUB_CHANNEL, user.id)
    except UserNotParticipant:
        try:
            # Generate invite link
            invite_link = await client.create_chat_invite_link(FORCE_SUB_CHANNEL)
            await message.reply(
                f"**You must join my updates channel to use me!**\n\n👉 [Join Channel]({invite_link.invite_link})",
                disable_web_page_preview=True,
                quote=True
            )
        except ChatAdminRequired:
            await message.reply(
                "Bot is not admin in the force sub channel. Please make it admin and try again.",
                quote=True
            )
        return

    # Welcome message
    welcome_text = (
        f"**Hᴇʟʟᴏ {user.mention} 👋,**\n"
        "I'ᴍ Lᴀᴛᴇꜱᴛ Aᴅᴠᴀɴᴄᴇᴅ & Pᴏᴡᴇʀꜰᴜʟ Aᴜᴛᴏ Fɪʟᴛᴇʀ Bᴏᴛ.\n"
        "Yᴏᴜ Cᴀɴ Uꜱᴇ Mᴇ Tᴏ Gᴇᴛ Mᴏᴠɪᴇs🍿 [Jᴜsᴛ Sᴇɴᴅ Mᴇ Mᴏᴠɪᴇ Nᴀᴍᴇ]\n"
        "Oʀ Yᴏᴜ Cᴀɴ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ & Mᴀɢɪᴄ Hᴀᴘᴘᴇɴs!"
    )
    await message.reply(welcome_text, quote=True)

# Run both Flask and Bot
import threading

def run_flask():
    app.run(host="0.0.0.0", port=8000)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run()
