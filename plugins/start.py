import os
import asyncio
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, ChannelInvalid
from config import START_MSG, FORCE_MSG
from bot import Bot
from helper_func import subscribed, encode, decode, get_messages
from database.database import (
    add_user, del_user, full_userbase, present_user, 
    get_admin_list, add_admin, remove_admin, 
    set_force_sub_channel, get_force_sub_channel
)

# Function for checking admin dynamically
async def is_admin(user_id):
    admin_list = await get_admin_list()
    return user_id in admin_list

@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass
    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return
        string = await decode(base64_string)
        argument = string.split("-")
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return
            ids = range(start, end + 1) if start <= end else [i for i in range(start, end - 1, -1)]
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except:
                return
        temp_msg = await message.reply("Please wait...")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something went wrong..!")
            return
        await temp_msg.delete()

        for msg in messages:
            caption = "" if not msg.caption else msg.caption.html

            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

            try:
                await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                await asyncio.sleep(0.5)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
            except:
                pass
        return
    else:
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("😊 About Me", callback_data="about"),
                    InlineKeyboardButton("🔒 Close", callback_data="close")
                ]
            ]
        )
        await message.reply_text(
            text=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            quote=True
        )
        return

@Bot.on_message(filters.command('setchannel') & filters.private)
async def set_channel(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("You are not authorized to perform this action.")
    
    channel_id = message.text.split(" ", 1)
    if len(channel_id) != 2 or not channel_id[1].isdigit():
        return await message.reply("Usage: /setchannel <channel_id>")
    
    channel_id = int(channel_id[1])
    
    try:
        channel_info = await client.get_chat(channel_id)
        channel_name = channel_info.title
        await set_force_sub_channel(channel_id)
        await message.reply(f"Channel set to: {channel_name} (ID: {channel_id})")
    except ChannelInvalid:
        await message.reply("The provided channel ID is invalid. Please check and try again.")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")

@Bot.on_message(filters.command('getchannel') & filters.private)
async def get_channel(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("You are not authorized to perform this action.")
    
    channel_id = await get_force_sub_channel()
    if channel_id is None:
        await message.reply("No force subscription channel set.")
        return
    
    try:
        channel_info = await client.get_chat(channel_id)
        channel_name = channel_info.title
        await message.reply(f"The current force subscription channel is: {channel_name} (ID: {channel_id})")
    except Exception as e:
        await message.reply(f"An error occurred while fetching the channel: {str(e)}")

@Bot.on_message(filters.command('promote') & filters.private)
async def promote_admin(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("You are not authorized to perform this action.")
    
    user_id = message.text.split(" ", 1)
    if len(user_id) != 2 or not user_id[1].isdigit():
        return await message.reply("Usage: /promote <user_id>")
    
    await add_admin(int(user_id[1]))
    await message.reply(f"User {user_id[1]} promoted to admin.")

@Bot.on_message(filters.command('demote') & filters.private)
async def demote_admin(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("You are not authorized to perform this action.")
    
    user_id = message.text.split(" ", 1)
    if len(user_id) != 2 or not user_id[1].isdigit():
        return await message.reply("Usage: /demote <user_id>")
    
    await remove_admin(int(user_id[1]))
    await message.reply(f"User {user_id[1]} demoted from admin.")

@Bot.on_message(filters.command('removechannel') & filters.private)
async def remove_channel(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("You are not authorized to perform this action.")
    
    await set_force_sub_channel(None)  # Set channel to None to remove it
    await message.reply("Force subscription channel removed.")

@Bot.on_message(filters.command('users') & filters.private)
async def get_users(client: Bot, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("You are not authorized to perform this action.")
    
    msg = await client.send_message(chat_id=message.chat.id, text="Processing ...")
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")

@Bot.on_message(filters.private & filters.command('broadcast'))
async def send_text(client: Bot, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("You are not authorized to perform this action.")
    
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total, successful, blocked, deleted, unsuccessful = 0, 0, 0, 0, 0

        pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1

        status = f"""<b><u>Broadcast Completed</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""

        return await pls_wait.edit(status)

    else:
        msg = await message.reply("Reply to a message to broadcast.")
        await asyncio.sleep(8)
        await msg.delete()
