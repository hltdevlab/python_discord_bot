import system_message
from dotenv import dotenv_values

env = {}
runtime = {
    'bot_name': '',
    'system_message': ''
}


def init():
    env = dotenv_values(".env")
    print(env)
    print('config initialised.')


def get_system_message():
    if runtime['bot_name'] == '':
        return ''

    # load system message from file if it has not been initialised    
    if runtime['system_message'] == '':
        runtime['system_message'] = system_message.load(bot_name=bot_name)
    
    return runtime['system_message']
