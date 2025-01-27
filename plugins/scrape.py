import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from helper_func import encode, get_message_id
from config import ADMINS, CHANNEL_ID  # Assuming DB_CHANNEL_ID is your database channel's ID

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('scrape'))
async def scrape_content(client: Client, message: Message):
    # Ask the admin to provide the link from the other bot
    try:
        link_message = await client.ask(
            text="Please provide the link of the content you want to scrape.",
            chat_id=message.from_user.id,
            timeout=60
        )
    except:
        return
    
    # Extract message ID from the provided link
    msg_id = await get_message_id(client, link_message)
    if msg_id:
        try:
            # Fetch the message content from the source bot using the extracted message ID
            source_message = await client.get_messages(
                chat_id=link_message.forward_from_chat.id,
                message_ids=msg_id
            )

            # Process the content (media, text, etc.)
            caption = source_message.caption if source_message.caption else "No caption provided."
            media = source_message.document or source_message.photo or source_message.video

            # Prepare the new message with the image provided by the admin
            new_caption = f"Scraped Content:\n\n{caption}"
            photo_url = "https://example.com/path/to/your/image.jpg"  # Admin-defined image URL or local path

            # Generate the new bot link using the current message ID and client information
            base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
            link = f"https://t.me/{client.username}?start={base64_string}"

            # Prepare the inline button for the scraped link
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]
            ])

            # Send the scraped message to the admin's bot
            if media:
                # If media exists, send it with the new caption
                await client.send_photo(
                    chat_id=message.from_user.id,
                    photo=media.file_id,  # If you want to send the file directly
                    caption=new_caption,
                    reply_markup=reply_markup
                )
            else:
                # If no media, just send the text
                await client.send_message(
                    chat_id=message.from_user.id,
                    text=new_caption,
                    reply_markup=reply_markup
                )

            # Send the scraped content to the database channel
            if media:
                # Post media to the database channel
                await client.send_photo(
                    chat_id=DB_CHANNEL_ID,
                    photo=media.file_id,
                    caption=new_caption,
                    reply_markup=reply_markup
                )
            else:
                # If no media, post the text to the database channel
                await client.send_message(
                    chat_id=DB_CHANNEL_ID,
                    text=new_caption,
                    reply_markup=reply_markup
                )

            # Notify the admin that the content was scraped successfully
            await message.reply("Content scraped and converted into your bot's link successfully.", quote=True)
        except FloodWait as e:
            await asyncio.sleep(e.x)
            await scrape_content(client, message)  # Retry the operation after waiting
        except Exception as e:
            print(e)
            await message.reply("An error occurred while processing the request.", quote=True)
    else:
        await message.reply("Invalid or unsupported link. Please provide a valid bot link.", quote=True)
