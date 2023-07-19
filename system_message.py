from datetime import datetime

# system_message.txt - for OpenAI
# system_message__palm_api.txt for Palm API

def load(file_path='system_message__palm_api.txt', bot_name=''):
    # legacy system_message.load()
    # upgrade to use system_message.get_system_message() instead.
    try:
        with open(file_path, 'r') as file:
            system_message = file.read()
            datetime_now = datetime.now().strftime("%d %b %Y %H:%M:%S")
            formatted_text = system_message.format(bot_name=bot_name, datetime_now=datetime_now)
            return formatted_text
        
    except FileNotFoundError:
        error_message = "Error: The specified file '{}' does not exist. Returning empty string.".format(file_path)
        print(error_message)
        return ''


def load_template(file_path='system_message__palm_api.txt'):
    print('load_template() ...')
    print('file_path: ', file_path)
    try:
        with open(file_path, 'r') as file:
            system_message_template = file.read()
            print('system_message_template: ', system_message_template)
            print('-----')
            return system_message_template
        
    except FileNotFoundError:
        error_message = "Error: The specified file '{}' does not exist. Returning empty string.".format(file_path)
        print(error_message)
        return ''


def get_system_message(system_message_template, bot_name=''):
    try:
        datetime_now = datetime.now().strftime("%d %b %Y %H:%M:%S")
        formatted_text = system_message_template.format(bot_name=bot_name, datetime_now=datetime_now)
        return formatted_text    
        
    except:
        error_message = "Error: Error formatting system message. Returning empty string."
        print(error_message)
        return ''
