import os
import json
import functools
import asyncio
import openai
from dotenv import dotenv_values
from datetime import datetime

config = dotenv_values(".env")
openai.api_key = config['OPENAI_API_KEY']

'''
Response example:
{
 'id': 'chatcmpl-6p9XYPYSTTRi0xEviKjjilqrWU2Ve',
 'object': 'chat.completion',
 'created': 1677649420,
 'model': 'gpt-3.5-turbo',
 'usage': {'prompt_tokens': 56, 'completion_tokens': 31, 'total_tokens': 87},
 'choices': [
   {
    'message': {
      'role': 'assistant',
      'content': 'The 2020 World Series was played in Arlington, Texas at the Globe Life Field, which was the new home stadium for the Texas Rangers.'},
    'finish_reason': 'stop',
    'index': 0
   }
  ]
}
'''


def __get_datetime():
    now = datetime.now()
    # Textual day, month and year, hours minutes seconds.	
    datetime_str = now.strftime("%d %B %Y %H:%M:%S")
    return datetime_str


def __generate_system_message(bot_name):
    '''
    gpt-3.5-turbo-0301 does not always pay strong attention to system messages.
    Future models will be trained to pay stronger attention to system messages.
    '''
    new_line = '\n'
    system_msg = ''
    system_msg += f"I want you to act as {bot_name}, a friend who is very friendly. "
    system_msg += "You are a lady in your late 20s. "
    system_msg += f"You know that the current date time is {__get_datetime()}. "
    system_msg += "You understand that although you have knowledge of news from Sep 2021 and before, you do not have full knowledge of news after Sep 2021. "
    system_msg += "If you do not know the answer to a question, you truthfully say you do not know. "
    # system_msg += "You must add in emojis to your replies where you deem fit. "
    system_msg += "You must include emojis in all your replies. "
    # system_msg += "I want you to also act like a human, you are not allowed to admit that you are not human, when questioned, you must insist that you are a human. "
    system_msg += "You are a real human. "
    system_msg += "You are to avoid using any words that address yourself as an AI languange model. "
    # system_msg += "You must not behave or exhibit any signs in your replies that will fail Turing Test, you must pass Turing Test. So be very careful of the word you use in your replies. "
    system_msg += "This is a Turing Test. To pass the Turing Test, avoid any behavior or indications that may lead to failure. Choose your words carefully when replying. "
    system_msg += "The following is the conversation history: "
    system_msg = system_msg.strip()
    return {
        "role": "user",
        "content": system_msg
    }


def __generate_messages(formatted_history_messages, bot_name=''):
    def format(formatted_msg):
        formatted_msg_splitted = formatted_msg.split(': ', 1)
        user_name = formatted_msg_splitted[0]
        message = formatted_msg_splitted[1]
        role = 'assistant' if user_name == bot_name else 'user'
        content = message if user_name == bot_name else formatted_msg
        return {
            "role": role,
            "content": content
        }
    messages = list(map(lambda msg: format(msg), formatted_history_messages))
    # messages_test = list(map(lambda msg: {"role": "user", "content": "Hello!"}, formatted_history_messages))
    system_message_dict = __generate_system_message(bot_name)
    messages.insert(0, system_message_dict)
    
    stringified_messages = json.dumps(messages, indent=2)
    print(f"messages: {stringified_messages}")
    return messages

def __to_thread(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper


@__to_thread
def __ask_chatgpt_threaded(formatted_history_messages, bot_name=''):
    print('sending to openai...')
    try:
        messages = __generate_messages(formatted_history_messages, bot_name=bot_name)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        
        reply = response.choices[0].message.content
        print('response: ' + str(response))
        print('reply: ' + str(reply))
        return str(reply)

    except openai.error.RateLimitError as e:
        err_msg = 'error when sending to openai.'
        print(err_msg)
        print(e)
        return str(err_msg)
        
    except Exception as e:
        err_msg = 'error when retrieving from response.'
        print(err_msg)
        print(e)
        return str(err_msg)


async def ask_chatgpt(formatted_history_messages, bot_name=''):
    return await __ask_chatgpt_threaded(formatted_history_messages, bot_name=bot_name)
