import discord
import random
import asyncio
from dotenv import dotenv_values
import config
import responses
import preset_command_handler
# import chatgpt
import chatgpt_gpt_3_5_turbo as chatgpt
import llm_model.palm_api_handler as llm

#config = dotenv_values(".env")
# config.init()
# print(f"config.env at bot: {config.env}")

async def send_message(message, user_message, is_private, formatted_history_messages=[]):
    try:
        response = responses.handle_response(user_message, formatted_history_messages=formatted_history_messages)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


async def send_reply(message, reply, is_private):
    is_tts = config.runtime['is_tts']
    print(f"message.channel: {message.channel}")
    print(f"is_private: {is_private}")
    print(f"reply sending to discord: {reply}")
    try:
        await message.author.send(reply, tts=is_tts) if is_private else await message.channel.send(reply, tts=is_tts)
    except Exception as e:
        print(f"Error at send_reply(): {e}")


async def get_history(channel, limit=int(config.env['HISTORY_MESSAGES_COUNT'])):
    messages = [message async for message in channel.history(limit=limit)]
    # messages is now a list of Message...
    formatted_messages = format_history_messages(messages)
    formatted_messages.reverse()
    '''
    print('----- history -----')
    for msg in formatted_messages:
        print(msg)
        #print('msg.content: ' + msg.content)
    print('----------')
    '''
    return formatted_messages


def format_history_message(message):
    username = str(message.author.name)
    user_message = str(message.clean_content)
    return f"{username}: {user_message}"


def format_history_messages(messages):
    return list(map(lambda x: format_history_message(x), messages))


def is_to_reply_in_private(message):
    user_message = str(message.content)
    return user_message[0] == '?'


def get_reply_delay_in_sec(message):
    user_message = str(message.content)
    user_message_lower = user_message.lower()

    if config.runtime['is_urgent']:
        return 0
    
    if 'now' in user_message_lower:
        return 0

    return random.randint(1, 60)


def get_channels(client):
    # getting the channels the bot involves
    channels = []
    for guild in client.guilds:
        print("guild.name: ", guild.name)
        for channel in guild.channels:
            channels.append(channel)
    
    print("private channels len: ", len(client.private_channels))
    for channel in client.private_channels:
        print("channel.recipient.name: ", channel.recipient.name)

    channels = channels + list(client.private_channels)

    print("channels len: ", len(channels))
    return channels


async def reply_backlog_messages(client):
    bot_name = client.user.name
    print("bot_name: ", bot_name)

    # getting the channels the bot involves
    channels = get_channels(client)

    # category_channels are basically groupings of text and voice channel.
    # category_channels = list(filter(lambda channel: str(channel.type) == "category", channels))

    text_channels = list(filter(lambda channel: str(channel.type) == "text", channels))
    
    messages_to_reply = []
    for channel in text_channels:
        print(f"channel: {channel.name} ({channel.type})")
        # get last message
        messages = [message async for message in channel.history(limit=1)]
        if len(messages) == 0:
            continue
        
        message = messages[0]
        last_message_username = str(message.author.name)
        print("last_message_username: ", last_message_username)

        if last_message_username != bot_name:
            messages_to_reply.append(message)
    print("messages_to_reply len: ", len(messages_to_reply))

    # trigger on_message() for each messages
    for message in messages_to_reply:
        on_message(message)


def run_discord_bot():
    TOKEN = config.env['BOT_TOKEN']
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        config.init_bot_name(client.user.name)
        config.init_system_message()
        print(f'{client.user} is now running!')

        await reply_backlog_messages(client)


    async def on_message_old(message):
        async with message.channel.typing():
            if message.author == client.user:
                return

            username = str(message.author)
            user_message = str(message.content)
            channel = str(message.channel)

            formatted_history_messages = await get_history(message.channel)

            print(f"{username} said: '{user_message}' ({channel})")

            delay_in_sec = get_reply_delay_in_sec(message)
            print(f"waiting for {delay_in_sec} seconds...")
            await asyncio.sleep(delay_in_sec)

            if user_message[0] == '?':
                user_message = user_message[1:]
                await send_message(message, user_message, is_private=True, formatted_history_messages=formatted_history_messages)
            else:
                await send_message(message, user_message, is_private=False, formatted_history_messages=formatted_history_messages)


    @client.event
    async def on_message(message):
        if message.author == client.user:
            # if the bot's message, then ignore.
            return

        username = str(message.author)
        user_message = str(message.clean_content)
        channel = str(message.channel)
        if message.reference:
            reference_msg = message.reference.resolved.clean_content
            print(f"reference_msg: {reference_msg}")
        print(f"{username} said: '{user_message}' ({channel})")

        is_private = is_to_reply_in_private(message)
        if is_private:
            # remove the ? prefix.
            user_message = user_message[1:]

        # determine if message is a preset command or not.
        reply = preset_command_handler.get_reply(message)
        if reply:
            if type(reply) == list:
                replies = reply
                for each_reply in replies:
                    print(each_reply)
                    await send_reply(message, each_reply, is_private=is_private)
                return
            
            await send_reply(message, reply, is_private=is_private)
            return
        
        async with message.channel.typing():
            # add in some random delays
            delay_in_sec = get_reply_delay_in_sec(message)
            print(f"waiting for {delay_in_sec} seconds...")
            await asyncio.sleep(delay_in_sec)

            # process message and use the respective services.
            formatted_history_messages = await get_history(message.channel)
            if message.reference:
                ref_username = message.reference.resolved.author.name
                ref_message = reference_msg
                ref_entry = f"{ref_username}: Reference: {ref_message}"
                formatted_history_messages.insert(-1, ref_entry)

            reply = await llm.ask_llm(formatted_history_messages, bot_name=client.user.name)
            if reply and type(reply) == list:
                replies = reply
                for each_reply in replies:
                    await send_reply(message, each_reply, is_private=is_private)
                return
            else:
                await send_reply(message, reply, is_private=is_private)
                return


    client.run(TOKEN)
