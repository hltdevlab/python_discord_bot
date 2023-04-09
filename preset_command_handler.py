import random
import config

def __toggle_urgent():
    if 'is_urgent' not in config.runtime:
        config.runtime['is_urgent'] = False
    
    config.runtime['is_urgent'] = not config.runtime['is_urgent']
    return f"```is_urgent = {config.runtime['is_urgent']}```"


def __spam(message):
    user_message = str(message.clean_content)
    user_message_lower = user_message.lower()

    remaining_text = user_message_lower.replace('!spam', '').strip()
    array_length = 10
    if remaining_text != '':
        try:
            array_length = int(remaining_text)
        except ValueError:
            pass
    return ["." for x in range(array_length)]


def get_reply(message):
    user_message = str(message.content)
    user_message_lower = user_message.lower()

    if user_message_lower == '!roll':
        return str(random.randint(1, 6))
    
    if user_message_lower.startswith('!spam'):
        return __spam(message)
    
    if user_message_lower == '!toggle_urgent':
        return __toggle_urgent()

    if user_message_lower == '!help':
        return '`This is a help message that you can modify.`'

    return None
