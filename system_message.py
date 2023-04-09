import datetime

def load(file_path='system_message.txt', bot_name=''):
    try:
        with open(file_path, 'r') as file:
            system_message = file.read()
            datetime_now = datetime.datetime.now().strftime("%d %b %Y %H:%M:%S")
            formatted_text = system_message.format(bot_name=bot_name, datetime_now=datetime_now)
            return formatted_text
        
    except FileNotFoundError:
        error_message = "Error: The specified file '{}' does not exist. Returning empty string.".format(file_path)
        print(error_message)
        return ''
