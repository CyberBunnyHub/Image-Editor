from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
import os
import threading
import random
import asyncio

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running."

API_ID = int(os.getenv("API_ID", "14853951"))
API_HASH = os.getenv("API_HASH", "0a33bc287078d4dace12aaecc8e73545")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7845318227:AAFIWjneKzVu_MmAsNDkD3B6NvXzlbMdCgU")
FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL", "-1002614983879")

bot = Client("autofilter-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    user = message.from_user
    loading = await message.reply("🍿", quote=True)

    try:
        await client.get_chat_member(FORCE_SUB_CHANNEL, user.id)
    except UserNotParticipant:
        try:
            invite_link = await client.create_chat_invite_link(FORCE_SUB_CHANNEL)
        except ChatAdminRequired:
            await loading.delete()
            return await message.reply(
                "**❌ Bot is not admin in the updates channel. Please make it admin and try again.**"
            )
        await loading.delete()
        return await message.reply(
            "**🔒 You must join the bot's channel to use me!**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Join Channel", url=invite_link.invite_link)],
                [InlineKeyboardButton("🔁 Refresh", callback_data="refresh_force_sub")]
            ]),
            quote=True
        )

    await loading.delete()

    image_urls = [
        "https://i.ibb.co/cSkDcyQH/d2c3ffef1693.jpg",
        "https://i.ibb.co/KcD29Vw6/36ea5dbb65f5.jpg",
        "https://i.ibb.co/HpdYbs21/93eaa5026aa1.jpg"
    ]
    image_url = random.choice(image_urls)
    me = await client.get_me()

    caption = (
        f"**Hᴇʟʟᴏ {user.mention} 👋,**\n"
        "I'ᴍ Lᴀᴛᴇꜱᴛ Aᴅᴠᴀɴᴄᴇᴅ & Pᴏᴡᴇʀꜰᴜʟ Aᴜᴛᴏ Fɪʟᴛᴇʀ Bᴏᴛ.\n\n"
        "**🎬 Just send a movie name to get files.**\n"
        "**➕ Add me to your group and enjoy magic filters!**"
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me To Group", url=f"https://t.me/{me.username}?startgroup=true")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help"),
         InlineKeyboardButton("🧑‍💻 About", callback_data="about")],
        [InlineKeyboardButton("📢 Updates", url="https://t.me/YourUpdateChannel"),
         InlineKeyboardButton("🆘 Support", url="https://t.me/YourSupportChat")]
    ])

    await message.reply_photo(
        photo=image_url,
        caption=caption,
        reply_markup=buttons,
        quote=True
    )

@bot.on_callback_query(filters.regex("refresh_force_sub"))
async def refresh_subscription(client, callback_query):
    try:
        await client.get_chat_member(FORCE_SUB_CHANNEL, callback_query.from_user.id)
        await callback_query.message.delete()
        await start_cmd(client, callback_query.message)
    except UserNotParticipant:
        await callback_query.answer("❌ You're still not joined!", show_alert=True)

def run_flask():
    app.run(host="0.0.0.0", port=8000)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run()
