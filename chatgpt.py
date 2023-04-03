import os
import openai
from dotenv import dotenv_values

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

def generate_prompt(formatted_history_messages):
    bot_name = 'JustBot'
    prompt = f"I want you to act as {bot_name}, a friend who is very friendly, can reply in either English or Chinese. You are supposed to reply as {bot_name}."
    prompt += f"The followings are the conversation history: {'\n'.join(formatted_history_messages)}"
    print('prompt: ' + prompt)
    return prompt


def ask_chatgpt(formatted_history_messages):
    print('sending to openai...')
    prompt = generate_prompt()
    response = openai.Completion.create(
        model = "text-davinci-003",
        #model = "gpt-3.5-turbo",
        #prompt = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: Hello, who are you?\nAI: I am an AI created by OpenAI. How can I help you today?\nHuman: I'd like to cancel my subscription.\nAI:",
        prompt = prompt,
        temperature = 0.9,
        max_tokens = 150,
        top_p = 1,
        frequency_penalty = 0.0,
        presence_penalty = 0.6,
        stop = [" Human:", " AI:"]
    )

    try:
        print('response type: ' + str(type(response)))
        print('response: ' + str(response))
        # print('msg content: ' + str(response['choices'][0]['message']['content']))
        print('text: ' + str(response['choices'][0]['text']))
        return str(response['choices'][0]['text'])
    except Exception as e:
        print('error when retrieving from response.')
        print(e)
        return str('error when retrieving from response.')
