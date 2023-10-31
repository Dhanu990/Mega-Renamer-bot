import os
from pyrogram import Client, filters
from pyrogram.types import Message
import sqlite3

# Initialize your Pyrogram client
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
app = Client("renamer_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Initialize a SQLite database to store file_id to new name mappings
db = sqlite3.connect("file_mappings.db")
cursor = db.cursor()

# Check if the table for file mappings exists, and create it if not
cursor.execute("CREATE TABLE IF NOT EXISTS file_mappings (file_id TEXT, new_name TEXT)")
db.commit()

# Function to add a file_id to new name mapping
def add_file_mapping(file_id, new_name):
    cursor.execute("INSERT INTO file_mappings (file_id, new_name) VALUES (?, ?)", (file_id, new_name))
    db.commit()

# Function to get the new name for a given file_id
def get_new_name(file_id):
    cursor.execute("SELECT new_name FROM file_mappings WHERE file_id = ?", (file_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

# Command to rename a file (you can modify this as needed)
@app.on_message(filters.command("rename", prefixes="/") & filters.private)
async def rename_file(_, message: Message):
    if message.reply_to_message and message.reply_to_message.document:
        new_name = message.text.split(maxsplit=1)
        if len(new_name) > 1:
            new_name = new_name[1]
            file_id = message.reply_to_message.document.file_id
            add_file_mapping(file_id, new_name)
            await message.reply(f"Renamed file with ID {file_id} to {new_name}")
        else:
            await message.reply("Please provide a new name for the file.")
    else:
        await message.reply("Please reply to a document to rename it.")

# Command to get a renamed file (you can modify this as needed)
@app.on_message(filters.command("get", prefixes="/") & filters.private)
async def get_renamed_file(_, message: Message):
    if message.reply_to_message and message.reply_to_message.document:
        file_id = message.reply_to_message.document.file_id
        new_name = get_new_name(file_id)
        if new_name:
            await message.reply_document(file_id, caption=new_name)
        else:
            await message.reply("This file has not been renamed.")
    else:
        await message.reply("Please reply to a document to get it.")

# Start the bot
app.run()
