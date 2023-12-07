from openai import OpenAI
import os
import json

with open('key.json', 'r') as f:
    key = json.load(f)['OPENAI_API_KEY']

model = 'gpt-4-1106-preview'
client = OpenAI(api_key=key)


snippit = 'On _%#MMDD2007#%_ if ok with Dr. _%#NAME#%_, increase Lovenox to 100 mg subcu b.i.d. Discontinue Lovenox 24 hours prior to next surgery on _%#MMDD2007#%_. Will hold aspirin and Coumadin until after next scheduled surgery on _%#MMDD2007#%_. 3. Hypertension, controlled. Hold Lopressor, Lasix, spironolactone for SBP less than 110. Hold metoprolol for pulse less than 55. 4. Diabetes type 2, currently controlled. Hold glyburide for blood sugar less than 100. Change IV fluid to normal saline plus 20 KCl at 125 ml per hour.'

in_prompt = f'''
    Create a bulleted list of all medications mentioned in the clinical snippit below. Include the medication status as a single word: "active", "discontinued", or "neither".
    Provide evidence for each choice in the following format:

    - Medication_1 (status): Evidence_1
    - Medication_2 (status): Evidence_2
    - Medication_3 (status): Evidence_3

    We will refer to this as "LIST A"
    Snippit: {snippit}
'''

out_prompt = '''
    Based on the evidence provided, verify the accuracy of each choice. Reclassify any incorrect medications.
    Create a new bulleted list in the following format, where the status is a single word, "active", "discontinued", or "neither". 
    Do not include evidence in this list

    - Medication_1 (status)
    - Medication_2 (status)
    - Medication_3 (status)

    We will refer to this as "LIST B"

    Return the output in the following format

    LIST A
    
    LIST B
'''

response = client.chat.completions.create(
    model=model,
    messages=[
        {'role': 'system', 'content': 'You are a medical information extraction assistant. Your job is to extract the status of medicine from clinical snippits'},
        {'role': 'user', 'content': in_prompt},
        {'role': 'user', 'content': 'Based on your response, go back and search for any omitted medications. Be sure to provide evidence for each'},
        {'role': 'user', 'content': out_prompt}
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
