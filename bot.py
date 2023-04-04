import discord
import random
import time
from dotenv import dotenv_values
import responses
import preset_command_handler
import chatgpt

config = dotenv_values(".env")


async def send_message(message, user_message, is_private, formatted_history_messages=[]):
    try:
        response = responses.handle_response(user_message, formatted_history_messages=formatted_history_messages)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


async def send_reply(message, reply, is_private):
    try:
        await message.author.send(reply) if is_private else await message.channel.send(reply)
    except Exception as e:
        print(e)


async def get_history(channel, limit=10):
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
    user_message = str(message.content)
    return f"{username}: {user_message}"


def format_history_messages(messages):
    return list(map(lambda x: format_history_message(x), messages))


def is_to_reply_in_private(message):
    user_message = str(message.content)
    return user_message[0] == '?'


def get_reply_delay_in_sec(message):
    user_message = str(message.content)
    user_message_lower = user_message.lower()

    if 'now' in user_message_lower:
        return 0

    return random.randint(1, 60)


def run_discord_bot():
    TOKEN = config['BOT_TOKEN']
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')


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
            time.sleep(delay_in_sec)

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
        user_message = str(message.content)
        channel = str(message.channel)
        print(f"{username} said: '{user_message}' ({channel})")

        is_private = is_to_reply_in_private(message)
        if is_private:
            # remove the ? prefix.
            user_message = user_message[1:]

        # determine if message is a preset command or not.
        reply = preset_command_handler.get_reply(message)
        if reply:
            if type(reply) == 'list':
                replies = reply
                for each_reply in replies:
                    await send_reply(message, each_reply, is_private=is_private)
            
            await send_reply(message, reply, is_private=is_private)
            return
        
        async with message.channel.typing():
            # add in some random delays
            delay_in_sec = get_reply_delay_in_sec(message)
            print(f"waiting for {delay_in_sec} seconds...")
            time.sleep(delay_in_sec)

            # process message and use the respective services.
            formatted_history_messages = await get_history(message.channel)
            reply = chatgpt.ask_chatgpt(formatted_history_messages)
            if reply:
                await send_reply(message, reply, is_private=is_private)
                return


    client.run(TOKEN)
