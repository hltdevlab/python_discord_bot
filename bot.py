import discord
import responses
from dotenv import dotenv_values

config = dotenv_values(".env")


async def send_message(message, user_message, is_private, formatted_history_messages=[]):
    try:
        response = responses.handle_response(user_message, formatted_history_messages=formatted_history_messages)
        await message.author.send(response) if is_private else await message.channel.send(response)
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


def run_discord_bot():
    TOKEN = config['BOT_TOKEN']
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')


    @client.event
    async def on_message(message):
        async with message.channel.typing():
            if message.author == client.user:
                return

            username = str(message.author)
            user_message = str(message.content)
            channel = str(message.channel)

            formatted_history_messages = await get_history(message.channel)

            print(f"{username} said: '{user_message}' ({channel})")

            if user_message[0] == '?':
                user_message = user_message[1:]
                await send_message(message, user_message, is_private=True, formatted_history_messages=formatted_history_messages)
            else:
                await send_message(message, user_message, is_private=False, formatted_history_messages=formatted_history_messages)


    client.run(TOKEN)
