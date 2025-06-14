from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatJoinRequest,
    ChatMemberUpdated, InputMediaPhoto
)
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
from pymongo import MongoClient
from bson import ObjectId
import os
import threading
import random
import asyncio
from collections import defaultdict

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running."

API_ID = int(os.getenv("API_ID", "14853951"))
API_HASH = os.getenv("API_HASH", "0a33bc287078d4dace12aaecc8e73545")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7845318227:AAFIWjneKzVu_MmAsNDkD3B6NvXzlbMdCgU")
FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL", "-1002614983879")
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://CyberBunny:Bunny2008@cyberbunny.5yyorwj.mongodb.net/?retryWrites=true&w=majority")
DB_NAME = os.getenv("DB_NAME", "CyberBunny")

mongo = MongoClient(MONGO_URI)
db = mongo[DB_NAME]
movies_collection = db["CBI"]

bot = Client("autofilter-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.private & filters.command("start"))
async def start_cmd(client: Client, message: Message):
    args = message.text.split()
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

    if len(args) > 1 and args[1].startswith("get_"):
        file_id = args[1][4:]
        movie = movies_collection.find_one({"files.file_id": file_id})
        if not movie:
            return await message.reply("❌ File not found.")
        for file in movie["files"]:
            if file["file_id"] == file_id:
                return await message.reply_document(
                    document=file["file_id"],
                    caption=f"`{file['file_name']}`",
                    parse_mode=ParseMode.MARKDOWN
                )
        return

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

@bot.on_message(filters.private & filters.text & ~filters.command(["start", "help", "about"]))
async def handle_movie_query(client: Client, message: Message):
    if message.from_user.is_bot:
        return
    title_query = message.text.strip().lower()
    result = movies_collection.find_one({"title": {"$regex": f"^{title_query}$", "$options": "i"}})
    if not result:
        return await message.reply("❌ Movie not found in database.")
    lang_buttons = []
    files_by_lang = defaultdict(list)
    for file in result["files"]:
        files_by_lang[file["language"]].append(file)
    for lang in files_by_lang:
        lang_buttons.append([InlineKeyboardButton(lang, callback_data=f"lang_{lang}_{result['_id']}")])
    await message.reply(
        f"🎬 Movie: `{result['title']}`\nSelect a language to view files:",
        reply_markup=InlineKeyboardMarkup(lang_buttons),
        parse_mode=ParseMode.MARKDOWN
    )

@bot.on_callback_query(filters.regex(r"^lang_(.+?)_(.+)$"))
async def send_files_by_language(client, callback_query):
    lang, movie_id = callback_query.matches[0].group(1), callback_query.matches[0].group(2)
    movie = movies_collection.find_one({"_id": ObjectId(movie_id)})
    if not movie:
        return await callback_query.answer("❌ Movie not found.", show_alert=True)
    files = [f for f in movie["files"] if f["language"] == lang]
    if not files:
        return await callback_query.answer("No files found for this language.", show_alert=True)
    buttons = []
    for f in files[:10]:
        buttons.append([InlineKeyboardButton(f"{f['file_name']}", callback_data=f"get_{f['file_id']}")])
    await callback_query.message.edit_text(
        f"🎬 `{movie['title']}` - **{lang}** Files:\nSelect a file to get it.",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.MARKDOWN
    )

@bot.on_callback_query(filters.regex(r"^get_(.+)$"))
async def send_file(client, callback_query):
    file_id = callback_query.matches[0].group(1)
    movie = movies_collection.find_one({"files.file_id": file_id})
    if not movie:
        return await callback_query.answer("❌ File not found.", show_alert=True)
    for file in movie["files"]:
        if file["file_id"] == file_id:
            await callback_query.message.reply_document(
                document=file["file_id"],
                caption=f"`{file['file_name']}`",
                parse_mode=ParseMode.MARKDOWN
            )
            return

@bot.on_callback_query(filters.regex("help"))
async def help_callback(client, callback_query):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("🔙 Back", callback_data="start_back")]
    ])
    await callback_query.message.edit_text(
        "<b>👋 Welcome to my store</b>\n\n<blockquote>Note: Under Construction 🚧</blockquote>",
        reply_markup=buttons,
        parse_mode=ParseMode.HTML
    )

@bot.on_callback_query(filters.regex("stats"))
async def stats_callback(client, callback_query):
    total_movies = movies_collection.count_documents({})
    total_files = 0
    languages = set()
    for movie in movies_collection.find():
        files = movie.get("files", [])
        total_files += len(files)
        for f in files:
            lang = f.get("language")
            if lang:
                languages.add(lang.lower())
    stats_text = (
        "<b>📊 Bot Stats:</b>\n\n"
        f"🎬 Total Movies: <code>{total_movies}</code>\n"
        f"📁 Total Files: <code>{total_files}</code>\n"
        f"🌐 Languages: <code>{', '.join(sorted(languages)) or 'N/A'}</code>\n"
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="help")]
    ])
    await callback_query.message.edit_text(
        stats_text,
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

@bot.on_message(filters.channel)
async def save_file_from_channel(client: Client, message: Message):
    if not message.document and not message.video:
        return
    caption = message.caption or ""
    lines = caption.splitlines()
    if len(lines) >= 1:
        if "🎬" in lines[0] and "|" in lines[0]:
            parts = lines[0].split("|")
            title = parts[0].replace("🎬", "").strip()
            language = parts[1].strip()
        else:
            title = "Unknown"
            language = "Unknown"
    else:
        title = "Unknown"
        language = "Unknown"
    file_info = {
        "file_id": message.document.file_id if message.document else message.video.file_id,
        "file_name": message.document.file_name if message.document else "Video.mp4",
        "language": language
    }
    existing = movies_collection.find_one({"title": title})
    if existing:
        if not any(f["file_id"] == file_info["file_id"] for f in existing["files"]):
            movies_collection.update_one(
                {"_id": existing["_id"]},
                {"$push": {"files": file_info}}
            )
    else:
        movies_collection.insert_one({
            "title": title,
            "files": [file_info]
        })

def run_flask():
    app.run(host="0.0.0.0", port=8000)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run()
