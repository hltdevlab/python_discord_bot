import random

def get_reply(message):
    user_message = str(message.content)
    user_message_lower = message.lower()

    if user_message_lower == '!roll':
        return str(random.randint(1, 6))

    if user_message_lower == '!help':
        return '`This is a help message that you can modify.`'

    return None
