# cbb.py

from pyrogram import __version__
from bot import Bot
from config import OWNER_ID, ADMINS, START_MSG, FORCE_MSG
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import add_admin, remove_admin, get_admin_list, get_force_sub_channel

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "about":
        await query.message.edit_text(
            text=f"<b>🤖 Bot Information:</b>\n\n"
                 f"👤 <b>Creator:</b> <a href='tg://user?id={OWNER_ID}'>This Person</a>\n"
                 f"📜 <b>Language:</b> <code>Python 3</code>\n"
                 f"📚 <b>Library:</b> <a href='https://docs.pyrogram.org/'>Pyrogram asyncio {__version__}</a>\n"
                 f"🔗 <b>Source Code:</b> <a href='https://github.com/CodeXBotz/File-Sharing-Bot'>Click here</a>\n"
                 f"📢 <b>Channel:</b> @CodeXBotz\n"
                 f"💬 <b>Support Group:</b> @CodeXBotzSupport\n\n"
                 f"✨ <b>Thank you for using our bot!</b>",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔒 Close", callback_data="close")
                    ]
                ]
            )
        )
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

# New command to promote an admin
@Bot.on_message(filters.command('promote') & filters.user(ADMINS))
async def promote_admin(client: Bot, message: Message):
    if len(message.command) < 2:
        await message.reply("❌ Usage: /promote <user_id>\n\nExample: /promote 123456789")
        return
    user_id = int(message.command[1])
    await add_admin(user_id)  # Assuming add_admin function handles adding to DB
    await message.reply(f"✅ User <code>{user_id}</code> has been promoted to admin.")

# New command to demote an admin
@Bot.on_message(filters.command('demote') & filters.user(ADMINS))
async def demote_admin(client: Bot, message: Message):
    if len(message.command) < 2:
        await message.reply("❌ Usage: /demote <user_id>\n\nExample: /demote 123456789")
        return
    user_id = int(message.command[1])
    await remove_admin(user_id)  # Assuming remove_admin function handles removing from DB
    await message.reply(f"❌ User <code>{user_id}</code> has been demoted from admin.")

# New command to set the force subscription channel
@Bot.on_message(filters.command('setchannel') & filters.user(ADMINS))
async def set_channel(client: Bot, message: Message):
    if len(message.command) < 2:
        await message.reply("❌ Usage: /setchannel <channel_id>\n\nExample: /setchannel -1001234567890")
        return
    channel_id = message.command[1]
    await set_force_sub_channel(channel_id)  # Function to set the channel ID in the database
    await message.reply(f"📺 The force subscription channel has been set to <code>{channel_id}</code>.")

# New command to get the current force subscription channel
@Bot.on_message(filters.command('getchannel') & filters.user(ADMINS))
async def get_channel(client: Bot, message: Message):
    channel_id = await get_force_sub_channel()  # Fetching the current channel ID from the database
    if channel_id:
        await message.reply(f"📺 The current force subscription channel is <code>{channel_id}</code>.")
    else:
        await message.reply("❌ No channel has been set.")

# New command to list all admins
@Bot.on_message(filters.command('adminlist') & filters.user(ADMINS))
async def admin_list(client: Bot, message: Message):
    admins = await get_admin_list()  # Fetching the list of admin user IDs
    if admins:
        admin_list_text = "👮‍♂️ Admins:\n" + "\n".join(f"<code>{admin_id}</code>" for admin_id in admins)
        await message.reply(admin_list_text)
    else:
        await message.reply("❌ No admins have been set.")
