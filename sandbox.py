from openai import OpenAI
import os
import json

with open('key.json', 'r') as f:
    key = json.load(f)['OPENAI_API_KEY']


client = OpenAI(api_key=key)

# gpt-4-1106-preview

response = client.chat.completions.create(
    model='gpt-4-1106-preview',
    response_format={'type': 'json_object'},
    messages=[
        {'role': 'system', 'content': 'You are a medical information extraction assistant. Your job is to extract medicine information in JSON format'},
        {'role': 'user', 'content': 'Prompt: From the following text note, extract all active and discontinued medicine.\
         Text: We recommended the patient stop using Tylenol and switch to Ibuprofen. We also recommend she take trenbolone twice daily'},
        {'role': 'user', 'content': 'Based on your response from the last request, provide a justification for each medication listed'}
    ]
)

content = response.choices[0].message.content

print(content)

with open('test.txt', 'w') as f:
    f.write(content)
