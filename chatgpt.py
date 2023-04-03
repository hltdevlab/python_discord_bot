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

def ask_chatgpt(message):
    response = openai.Completion.create(
        model = "text-davinci-003",
        prompt = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: Hello, who are you?\nAI: I am an AI created by OpenAI. How can I help you today?\nHuman: I'd like to cancel my subscription.\nAI:",
        temperature = 0.9,
        max_tokens = 150,
        top_p = 1,
        frequency_penalty = 0.0,
        presence_penalty = 0.6,
        stop = [" Human:", " AI:"]
    )
    return response['choices'][0]['message']['content']
