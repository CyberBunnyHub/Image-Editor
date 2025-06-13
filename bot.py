from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatJoinRequest,
    ChatMemberUpdated, InputMediaPhoto
)
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, FloodWait
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
BOT_TOKEN = os.getenv("BOT_TOKEN", "your-bot-token")
FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL", "-1002614983879")

bot = Client("autofilter-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.private & filters.command("start"))
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
            return await message.reply("❌ Bot is not admin in the updates channel.")
        await loading.delete()
        return await message.reply(
            "🔒 You must join the channel to use this bot.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Join Channel", url=invite_link.invite_link)],
                [InlineKeyboardButton("🔁 Refresh", callback_data="refresh_force_sub")]
            ])
        )

    await loading.delete()
    me = await client.get_me()
    image_url = random.choice([
        "https://i.ibb.co/cSkDcyQH/d2c3ffef1693.jpg",
        "https://i.ibb.co/KcD29Vw6/36ea5dbb65f5.jpg",
        "https://i.ibb.co/HpdYbs21/93eaa5026aa1.jpg"
    ])
    caption = (
        f"**Hello {user.mention} 👋,**\n"
        "I'm the latest powerful auto filter bot.\n\n"
        "🎬 Send a movie name to get files.\n"
        "➕ Add me to your group to enable magic filters!"
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me To Group", url=f"https://t.me/{me.username}?startgroup=true")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help"),
         InlineKeyboardButton("🧑‍💻 About", callback_data="about")],
        [InlineKeyboardButton("📢 Updates", url="https://t.me/YourUpdateChannel"),
         InlineKeyboardButton("🆘 Support", url="https://t.me/YourSupportChat")]
    ])
    await message.reply_photo(photo=image_url, caption=caption, reply_markup=buttons, quote=True)

@bot.on_callback_query(filters.regex("help"))
async def help_callback(client, callback_query):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="start_back")]
    ])
    await callback_query.message.edit_text(
        "<b>👋 Welcome to my store</b>\n\n<blockquote>Note: Under Construction 🚧</blockquote>",
        reply_markup=buttons,
        parse_mode=ParseMode.HTML
    )

@bot.on_callback_query(filters.regex("about"))
async def about_callback(client, callback_query):
    me = await client.get_me()
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 Lord", url="https://t.me/YourUsername")],
        [InlineKeyboardButton("🔙 Back", callback_data="start_back")]
    ])
    about_text = (
        "─────── 🍿<b>About Me</b> ───────\n\n"
        "-ˋˏ✄ I'm an <a href='https://t.me/{0}'>Auto Filter Bot</a>\n"
        "-ˋˏ✄ Built with <a href='https://www.python.org/'>Python</a> & <a href='https://docs.pyrogram.org/'>Pyrogram</a>\n"
        "-ˋˏ✄ Database: <a href='https://www.mongodb.com/'>MongoDB</a>\n"
        "-ˋˏ✄ Bot Server: <a href='https://Render.com/'>Render</a>"
    ).format(me.username)

    await callback_query.message.edit_text(
        about_text,
        reply_markup=buttons,
        parse_mode=ParseMode.HTML
    )

@bot.on_callback_query(filters.regex("start_back"))
async def back_to_start(client, callback_query):
    me = await client.get_me()
    image_url = random.choice([
        "https://i.ibb.co/cSkDcyQH/d2c3ffef1693.jpg",
        "https://i.ibb.co/KcD29Vw6/36ea5dbb65f5.jpg",
        "https://i.ibb.co/HpdYbs21/93eaa5026aa1.jpg"
    ])
    caption = (
        f"**Hello {callback_query.from_user.mention} 👋,**\n"
        "I'm the latest powerful auto filter bot.\n\n"
        "🎬 Send a movie name to get files.\n"
        "➕ Add me to your group to enable magic filters!"
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me To Group", url=f"https://t.me/{me.username}?startgroup=true")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help"),
         InlineKeyboardButton("🧑‍💻 About", callback_data="about")],
        [InlineKeyboardButton("📢 Updates", url="https://t.me/YourUpdateChannel"),
         InlineKeyboardButton("🆘 Support", url="https://t.me/YourSupportChat")]
    ])
    media = InputMediaPhoto(media=image_url, caption=caption, parse_mode=ParseMode.MARKDOWN)
    await callback_query.message.edit_media(media, reply_markup=buttons)

@bot.on_callback_query(filters.regex("refresh_force_sub"))
async def refresh_subscription(client, callback_query):
    try:
        await client.get_chat_member(FORCE_SUB_CHANNEL, callback_query.from_user.id)
        await start_cmd(client, callback_query.message)
    except UserNotParticipant:
        await callback_query.answer("❌ You're still not joined!", show_alert=True)

@bot.on_chat_member_updated()
async def bot_added_to_group(client, member: ChatMemberUpdated):
    if member.new_chat_member and member.new_chat_member.user.is_self:
        await client.send_message(
            chat_id=member.chat.id,
            text="👋 Hello everyone! I'm an auto filter bot.\n\n💬 Just send the name of a movie or series.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ℹ️ Help", callback_data="help"),
                 InlineKeyboardButton("🧑‍💻 About", callback_data="about")]
            ])
        )

def run_flask():
    app.run(host="0.0.0.0", port=8000)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run()
