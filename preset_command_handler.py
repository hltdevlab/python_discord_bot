import random

def get_reply(message):
    user_message = str(message.content)
    user_message_lower = user_message.lower()

    if user_message_lower == '!roll':
        return str(random.randint(1, 6))
    
    if user_message_lower.startswith('!spam'):
        remaining_text = user_message_lower.replace('!spam', '').strip()
        array_length = 10
        if remaining_text != '':
            try:
                array_length = int(remaining_text)
            except ValueError:
                pass
        return ["." for x in range(array_length)]

    if user_message_lower == '!help':
        return '`This is a help message that you can modify.`'

    return None
