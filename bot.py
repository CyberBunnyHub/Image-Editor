from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
from pymongo import MongoClient
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
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")

mongo_client = MongoClient(MONGO_URL)
db = mongo_client["broadcast_bot"]
users_collection = db["users"]

bot = Client("autofilter-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    user = message.from_user

    users_collection.update_one(
        {"_id": user.id},
        {"$set": {
            "name": user.first_name,
            "username": user.username,
            "joined_at": message.date
        }},
        upsert=True
    )

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

@bot.on_callback_query(filters.regex("help"))
async def help_callback(client, callback_query):
    help_text = (
        "<b>👋 Welcome to my store</b>\n\n"
        "<blockquote>Note: Under Construction 🚧</blockquote>"
    )

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 Stats", callback_data="stats"),
            InlineKeyboardButton("🗄 Database", callback_data="database")
        ],
        [
            InlineKeyboardButton("👥 Admins", callback_data="admins"),
            InlineKeyboardButton("🔙 Back", callback_data="start_back")
        ]
    ])

    await callback_query.message.edit_text(
        help_text,
        reply_markup=buttons,
        parse_mode="html",
        disable_web_page_preview=True
    )

@bot.on_callback_query(filters.regex("about"))
async def about_callback(client, callback_query):
    me = await client.get_me()
    bot_username = me.username

    about_text = (
        "─────── 🍿<b>About Me</b> ───────\n\n"
        "-ˋˏ✄ Iᴍ Aɴ <a href='https://t.me/{0}'>Aᴜᴛᴏ Fɪʟᴛᴇʀ Bᴏᴛ</a>\n"
        "-ˋˏ✄ Bᴜɪʟᴛ Wɪᴛʜ 💌 <a href='https://www.python.org/'>Pʏᴛʜᴏɴ</a> & <a href='https://docs.pyrogram.org/'>Pʏʀᴏɢʀᴀᴍ</a>\n"
        "-ˋˏ✄ Dᴀᴛᴀʙᴀsᴇ : <a href='https://www.mongodb.com/'>MᴏɴɢᴏDB</a>\n"
        "-ˋˏ✄ Bᴏᴛ Sᴇʀᴠᴇʀ : <a href='https://Render.com/'>Rᴇɴᴅᴇʀ</a>"
    ).format(bot_username)

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 Lord", url="https://t.me/YourUsername")],
        [InlineKeyboardButton("🔙 Back", callback_data="start_back")]
    ])

    await callback_query.message.edit_text(
        about_text,
        reply_markup=buttons,
        parse_mode="html",
        disable_web_page_preview=True
    )

@bot.on_callback_query(filters.regex("start_back"))
async def back_to_start(client, callback_query):
    user = callback_query.from_user
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

    await callback_query.message.delete()
    await callback_query.message.chat.send_photo(
        photo=image_url,
        caption=caption,
        reply_markup=buttons
    )

@bot.on_message(filters.command("broadcast") & filters.private)
async def broadcast_cmd(client: Client, message: Message):
    if message.from_user.id != 123456789:  # Replace with your ID
        return await message.reply("You are not authorized to use this command.")

    if message.reply_to_message:
        broadcast_message = message.reply_to_message
    else:
        if len(message.command) < 2:
            return await message.reply("Usage: /broadcast <message> or reply to a message.")
        broadcast_message = message.text.split(None, 1)[1]

    status_msg = await message.reply("📡 Broadcasting...", quote=True)
    sent, failed = 0, 0

    for user in users_collection.find():
        try:
            if isinstance(broadcast_message, str):
                await client.send_message(user["_id"], broadcast_message)
            else:
                await broadcast_message.copy(user["_id"])
            sent += 1
        except:
            failed += 1

    await status_msg.edit_text(
        f"✅ <b>Broadcast completed</b>\n\n"
        f"👤 Sent: <code>{sent}</code>\n"
        f"❌ Failed: <code>{failed}</code>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("↩️ OK", callback_data="broadcast_done")]
        ]),
        parse_mode="html"
    )

@bot.on_callback_query(filters.regex("broadcast_done"))
async def broadcast_done_callback(client, callback_query):
    await callback_query.answer("Broadcast report closed.", show_alert=False)
    await callback_query.message.delete()

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
