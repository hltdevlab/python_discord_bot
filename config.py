import system_message
from dotenv import dotenv_values

env = {
    'env_loaded': False
}
runtime = {
    'bot_name': '',
    'system_message': '',
    'is_urgent': False
}


def init():
    if env['env_loaded']:
        return
    
    envOrderedDict = dotenv_values(".env")
    for key, value in envOrderedDict.items():
        env[key] = value
    
    env['env_loaded'] = True
    print('config initialised.')
    print('env loaded in memory.')


def init_bot_name(bot_name):
    runtime['bot_name'] = bot_name
    print('bot_name loaded in memory.')


def init_system_message():
    if runtime['bot_name'] == '':
        print('cannot init system message as bot_name is not defined.')

    # load system message from file if it has not been initialised    
    if runtime['system_message'] == '':
        bot_name = runtime['bot_name']
        runtime['system_message'] = system_message.load(bot_name=bot_name)
        print('system_message loaded in memory.')


# will read .env upon first imported this file
# .env will only load once.
# once loaded, it will remain in memory.
# subsequent access is read from memory.
init()
