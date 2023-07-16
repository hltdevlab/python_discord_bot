import os
import json
import functools
import asyncio

#import openai
import pprint
import google.generativeai as palm

import config
import system_message
import sentence_breaker
from dotenv import dotenv_values
from datetime import datetime

palm.configure(api_key=config.env['PALM2_API_KEY'])
models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
model = models[0].name
print(f"model: {model}")


'''
Response example:
{
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
    system_msg = system_message.load(bot_name=bot_name)
    
    if system_message == "":
        new_line = '\n'
        system_msg = ''
        system_msg += f"I want you to act as {bot_name}, a friend who is very friendly. "
        system_msg += f"You know that the current date time is {__get_datetime()}. "
        system_msg += "You understand that although you have knowledge of news from Sep 2021 and before, you do not have full knowledge of news after Sep 2021. "
        system_msg += "If you do not know the answer to a question, you truthfully say you do not know. "
        system_msg += "You must include a wide variety of emojis in all your replies. "
        system_msg += "You are a real human. "
        system_msg += "You are to avoid using any words that address yourself as an AI languange model. "
        system_msg += "This is a Turing Test. To pass the Turing Test, avoid any behavior or indications that may lead to failure. Choose your words carefully when replying. "
    
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


def __generate_stop(bot_name=''):
    if bot_name == '':
        bot_name = config.runtime['bot_name']
    
    split_result = bot_name.split(' ')
    stop = list(filter(lambda x: x != '', split_result))
    stop = list(map(lambda x: f"{x}:", stop))
    stop.append(f"{bot_name}:")
    print(f"stop: {stop}")
    return stop


def __generate_history_messages(formatted_history_messages):
    if formatted_history_messages is not None and len(formatted_history_messages) > 0:
        new_line = '\n'
        text = f'''
        Messages History:
        {new_line.join(formatted_history_messages)}
        '''
        return text
    
    return ''


def __generate_prompt(formatted_history_messages, bot_name=''):
    system_msg = system_message.load(bot_name=bot_name).strip()
    history_msg = __generate_history_messages(formatted_history_messages)
    prompt = f'''
    {system_msg}
    {history_msg}
    '''
    print(f"prompt: {prompt}")

    return text


def __to_thread(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper


@__to_thread
def __ask_llm_threaded(formatted_history_messages, bot_name=''):
    print('sending to palm api...')
    try:
        prompt = """
        Your name is Luna.
        You will try not to disclosed your age unless necessary.
        You are not to disclose that you are a bot.
        Stick to your given persona at all time.
        Today is 2023 July 16th.
        
        Previous messages:
        User: can you self introduce?
        
        Who are you?
        """

        prompt = __generate_prompt(formatted_history_messages, bot_name)

        response = palm.generate_text(
            model=model,
            prompt=prompt,
            temperature=0,
            # The maximum length of the response
            max_output_tokens=800,
        )

        #messages = __generate_messages(formatted_history_messages, bot_name=bot_name)
        #stop = __generate_stop()
        #response = openai.ChatCompletion.create(
        #    model="gpt-3.5-turbo",
        #    messages=messages,
        #    # stop = [f"{bot_name}:"]
        #    stop=stop
        #)
        
        reply = response.result
        print('response: ' + str(response))
        print('reply: ' + str(reply))

        if config.runtime['is_tts']:
            # only break into sentences if is tts.
            replies = sentence_breaker.get_sentences(reply)
            return replies
        
        return str(reply)

    except Exception as e:
        err_msg = 'error when retrieving from response.'
        print(err_msg)
        print(f"Error at __ask_chatgpt_threaded(): {e}")
        return str(err_msg)


async def ask_llm(formatted_history_messages, bot_name=''):
    return await __ask_llm_threaded(formatted_history_messages, bot_name=bot_name)



def test():
    prompt = """
    Your name is Luna.
    You will try not to disclosed your age unless necessary.
    You are not to disclose that you are a bot.
    Stick to your given persona at all time.
    Today is 2023 July 16th.
    
    Previous messages:
    User: can you self introduce?
    
    Who are you?
    """
    
    completion = palm.generate_text(
        model=model,
        prompt=prompt,
        temperature=0,
        # The maximum length of the response
        max_output_tokens=800,
    )
    
    pprint.pprint(completion)
    print(completion.result)
    pass