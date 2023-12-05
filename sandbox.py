from openai import OpenAI
import os
import json

with open('key.json', 'r') as f:
    key = json.load(f)['OPENAI_API_KEY']


client = OpenAI(api_key=key)

# gpt-4-1106-preview
prompt='She had hyperdynamic systole, and significant diastolic dysfunction. She had mild RVSP = 38 + CVP. No PDA was noted. Her preliminary cardiac measurements were as follows LVIDd 15, LVIDs 8, LVPWd 6-8, LA 12, aorta 12. Because of her hemodynamic instability, she was initially on dobutamine and Nipride. A trial of Esmolol was initiated, but quickly discontinued due to worsening respiratory status.'
response = client.chat.completions.create(
    model='gpt-4-1106-preview',
    response_format={'type': 'json_object'},
    messages=[
        {'role': 'system', 'content': 'You are a medical information extraction assistant. Your job is to extract medicine information in JSON format'},
        {'role': 'user', 'content': prompt},
        {'role': 'user', 'content': 'Based on your response, go back and search for any ACTIVE medications you may have missed. Again, provide justifications for each'},
        {'role': 'user', 'content': 'Based on your response, go back and search for any DISCONTINUED medications you may have missed. Again, provide justifications for each'},
        {'role': 'user', 'content': 'Double check each medication from your response and remove any incorrect choices based on the original discharge summary and your justifications. The should only contain all active and discontinued medications'}
    ]
)

print(response)
content = response.choices[0].message.content
tokens = response.usage.total_tokens

print(content)
print()
print(tokens)

with open('test.txt', 'w') as f:
    f.write(content)
