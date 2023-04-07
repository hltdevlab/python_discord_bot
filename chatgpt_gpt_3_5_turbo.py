import os
import json
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


def __generate_prompt(formatted_history_messages, bot_name=''):
    new_line = '\n'
    prompt = ''
    # prompt += f"I want you to act as {bot_name}, a friend who is very friendly, can reply in either English or Chinese. "
    prompt += f"I want you to act as {bot_name}, a friend who is very friendly. "
    # prompt += f"I want you to believe that the current date time is {get_datetime()}, but you knew your knowledge is only up-to-date till 2021. "
    prompt += "You are a lady in your late 20s."
    prompt += f"You know that the current date time is {__get_datetime()}. "
    prompt += "You understand that although you have knowledge of news from 2021 and before, you do not have full knowledge of news after 2021. "
    # prompt += f"You are supposed to reply as {bot_name}."
    # prompt += f"{bot_name} should reply in the same language as the current message in the conversation history. "
    # prompt += "Unless the current message is asking for translation, then other languages are allowed. "
    prompt += "I want you to also act like a human, you are not allowed to admit that you are not human, when questioned, you must insist that you are a human. "
    prompt += f"The followings are the conversation history:{new_line}{new_line.join(formatted_history_messages)}"
    prompt += f"{new_line}{bot_name}: "
    print('prompt: ' + prompt)
    return prompt


def __generate_system_message(bot_name):
    new_line = '\n'
    system_msg = ''
    system_msg += f"I want you to act as {bot_name}, a friend who is very friendly. "
    system_msg += "You are a lady in your late 20s."
    system_msg += f"You know that the current date time is {__get_datetime()}. "
    system_msg += "You understand that although you have knowledge of news from 2021 and before, you do not have full knowledge of news after September 2021. "
    system_msg += "I want you to also act like a human, you are not allowed to admit that you are not human, when questioned, you must insist that you are a human. "
    system_msg += "If you do not know the answer to a question, you truthfully say you do not know. "
    return {
        "role": "system",
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


def ask_chatgpt(formatted_history_messages, bot_name=''):
    print('sending to openai...')
    messages = __generate_messages(formatted_history_messages, bot_name=bot_name)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    try:
        reply = response.choices[0].message.content
        print('response: ' + str(response))
        print('reply: ' + str(reply))
        return str(reply)
    except Exception as e:
        print('error when retrieving from response.')
        print(e)
        return str('error when retrieving from response.')
