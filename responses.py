import random
from chatgpt import ask_chatgpt

def handle_response(message):
    p_message = message.lower()

    #if p_message == 'hello':
    #    return 'Hey there!'

    if p_message == 'roll':
        return str(random.randint(1, 6))

    if p_message == '!help':
        return '`This is a help message that you can modify.`'

    #return "I don't know what you said."
    
    return ask_chatgpt(message)
