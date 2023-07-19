import os
import json
import functools
import asyncio
import traceback

from pprint import pprint
import google.generativeai as palm

import config
import system_message
import sentence_breaker
from dotenv import dotenv_values
from datetime import datetime

palm.configure(api_key=config.env['PALM2_API_KEY'])

delimiter = ', '
all_models = palm.list_models()
all_models_name = list(map(lambda x: x.name, all_models))
print(f"all_models_name: {delimiter.join(all_models_name)}")

'''
chat_models = [m for m in all_models if m.name == 'models/chat-bison-001']
chat_model = chat_models[0].name if len(chat_models) > 1 else ''
print(f"chat_model: {chat_model}")

if len(chat_models) > 1:
    methods = chat_models[0].supported_generation_methods
    methods_str = ',\n'.join(methods)
    #print(f"methods_str: {methods_str}")
'''
 
print('--- loop through methods ---')
for m in all_models:
    methods = m.supported_generation_methods
    methods_str = ',\n'.join(methods)
    print(f'model name: {m.name}')
    print(f"methods_str: {methods_str}")
print('--- ---')

chat_models = [m for m in palm.list_models() if 'generateMessage' in m.supported_generation_methods]
chat_model = chat_models[0].name
print(f"chat_model in used: {chat_model}")

text_models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
text_model = text_models[0].name
print(f"text_model in used: {text_model}")

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
    system_msg = get_system_message(config.runtime['system_message_template'], bot_name=bot_name).strip()
    return system_msg


def __generate_messages(formatted_history_messages, bot_name=''):
    '''
    generate messages such that they are in alternating authors.
    there are only 2 authors, 0 is human, 1 is chatbot.
    '''
    # curr_* are the buffer to consolidate content of the same author.
    curr_author = ''
    curr_content = ''
    messages = []
    for formatted_msg in formatted_history_messages:
        formatted_msg_splitted = formatted_msg.split(': ', 1)
        user_name = formatted_msg_splitted[0]
        message = formatted_msg_splitted[1]

        # get the author and content of this iteration
        author = '1' if user_name == bot_name else '0'
        content = message if user_name == bot_name else formatted_msg

        if author != curr_author:
            # different author as previous iteration, author changed.
            if curr_content != '':
                # there are existing content in buffer, so commit it into messages.
                messages.append({
                    "author": curr_author,
                    "content": curr_content
                })

            # then reinitialise the buffer with author and content of this iteration
            curr_author = author
            curr_content = content
        
        else:
            # same author as previous iteration, so continue append content to buffer.
            curr_content = curr_content + '\n' + content

    # at the end of iteration, if there are content in buffer, commit it into messages.
    if curr_content != '':
        messages.append({
            "author": curr_author,
            "content": curr_content
        })
    
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
        history_messages = f'''
            Messages History:
            {new_line.join(formatted_history_messages)}
            '''.strip()

        print(f"history_messages: {history_messages}")
        return history_messages
    
    return ''


def __generate_prompt(formatted_history_messages, bot_name=''):
    #system_msg = system_message.load(bot_name=bot_name).strip()
    system_msg = __generate_system_message(bot_name)
    history_msg = __generate_history_messages(formatted_history_messages)
    prompt = f'''
        {system_msg}
        {history_msg}
        '''.strip()

    return prompt


def __get_llm_respose_obj__text_completion(formatted_history_messages, bot_name=''):
    prompt = __generate_prompt(formatted_history_messages, bot_name)

    response = palm.generate_text(
        model=text_model,
        prompt=prompt,
        temperature=0,
        # stop_sequences=[f"{bot_name}:"],
        # The maximum length of the response
        max_output_tokens=800,
    )

    print('response: ')
    pprint(response)
    
    return response


def __get_llm_reply__text_completion(response):
    if response.result is None:
        return ''
    
    reply = response.result
    return reply


def __palm_generate_text(formatted_history_messages, bot_name=''):
    response = __get_llm_respose_obj__text_completion(formatted_history_messages, bot_name)
    reply = __get_llm_reply__text_completion(response)
    return reply


def __get_llm_respose_obj(formatted_history_messages, bot_name=''):
    response = palm.chat(
        # model=chat_model, # default model for chat() is already chat-bison-001.
        context=__generate_system_message(bot_name),
        messages=__generate_messages(formatted_history_messages, bot_name),
        temperature=0.2
    )

    print('response: ')
    pprint(response)
    
    return response


def __get_llm_reply(response):
    if response.candidates is None or len(response.candidates) == 0:
        return ''
    
    reply = response.candidates[0]['content']
    return reply


def __palm_chat(formatted_history_messages, bot_name=''):
    response = __get_llm_respose_obj(formatted_history_messages, bot_name)
    reply = __get_llm_reply(response)
    return reply


def __to_thread(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper


@__to_thread
def __ask_llm_threaded(formatted_history_messages, bot_name=''):
    print('sending to palm api...')
    try:
        #response = __get_llm_respose_obj(formatted_history_messages, bot_name)
        #reply = __get_llm_reply(response)

        reply = __palm_chat(formatted_history_messages, bot_name)

        if reply == '':
            reply = __palm_generate_text(formatted_history_messages, bot_name)

        stop_sequences = __generate_stop()
        for stop in stop_sequences:
            if stop in reply:
                print(f'bot name ({stop}) found in reply, cleaning up...')
                unwanted_text, reply = reply.split(stop, maxsplit=1)
                reply = reply.strip()

        print('reply: ' + str(reply))

        if config.runtime['is_tts']:
            # only break into sentences if is tts.
            replies = sentence_breaker.get_sentences(reply)
            return replies
        
        return str(reply)

    except Exception as e:
        err_msg = 'error when retrieving from response.'
        print(err_msg)
        print(f"Error at __ask_llm_threaded(): {e}")
        traceback.print_exc()
        return str(err_msg)


async def ask_llm(formatted_history_messages, bot_name=''):
    return await __ask_llm_threaded(formatted_history_messages, bot_name=bot_name)
