import random

def get_reply(message):
    p_message = message.lower()

    if p_message == '!roll':
        return str(random.randint(1, 6))

    if p_message == '!help':
        return '`This is a help message that you can modify.`'

    return None
