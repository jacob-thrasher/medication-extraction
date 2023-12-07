from openai import OpenAI
import json
import os
import pandas as pd
import ast
from utils import *
from sklearn.metrics import f1_score

def single_call(client, note, model='gpt-4-1106-preview'):
    prompt = f'''
        Return a bulleted list of all medications mentioned in the clinical snippit below. Include the medication status as a single word: "active", "discontinued", or "neither". Use the following format:

        - Medication_1 (status)
        - Medication_2 (status)
        - Medication_3 (status)


        Snippit: {note}
    '''

    response = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': 'You are a medical information extraction assistant. Your job is to extract the status of medicine from clinical snippits'},
            {'role': 'user', 'content': prompt},
        ]
    )

    content = response.choices[0].message.content
    prompt_tokens = int(response.usage.prompt_tokens)
    completion_tokens = int(response.usage.completion_tokens)

    return content, prompt_tokens, completion_tokens




def self_feedback(client, note, model='gpt-4-1106-preview'):
    in_prompt = f'''
        Create a bulleted list of all medications mentioned in the clinical snippit below. Include the medication status as a single word: "active", "discontinued", or "neither".
        Provide evidence for each choice.
        Snippit: {note}
    '''
    
    out_prompt = '''
        Verify the accuracy of each choice by considering information from the original snippit that is outside the scope of the evidence provided. 
        Remove or reclassify any incorrect medications.
        Return a final bulleted list in the following format, where the status is a single word, "active", "discontinued", or "neither". 

        - Medication_1 (status)
        - Medication_2 (status)
        - Medication_3 (status)

        Do not include evidence in this list
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

    content = response.choices[0].message.content
    prompt_tokens = int(response.usage.prompt_tokens)
    completion_tokens = int(response.usage.completion_tokens)

    return content, prompt_tokens, completion_tokens

def run_experiment(csvpath, outpath, num_trials, experiment='single', model='gpt-4-1106-preview'):
    assert experiment in ['single', 'feedback'], f'type must be in [single, feedback], got {experiment}'

    with open('key.json', 'r') as f:
        key = json.load(f)['OPENAI_API_KEY']
    client = OpenAI(api_key=key)

    prompt_tokens = 0
    completion_tokens = 0

    df = pd.read_csv(csvpath)
    if num_trials > 0: df = df[:num_trials]
    num_trials = len(df)
    
    for i, row in df.iterrows():
        if not pd.isnull(row.response): continue 

        snippet = row.snippet
        index = row['index']

        if experiment == 'single': 
            response, p_tokens, c_tokens = single_call(client, snippet, model=model)
        elif experiment == 'feedback':
            response, p_tokens, c_tokens = self_feedback(client, snippet, model=model)

        print(f'Trial {i}/{num_trials}:')
        print(f'---> Input tokens used : {p_tokens}')
        print(f'---> Output tokens used: {c_tokens}')
        
        prompt_tokens += p_tokens
        completion_tokens += c_tokens

        df.loc[df['index']==index, 'response'] = response 
    
        df.to_csv(outpath)
    return prompt_tokens, completion_tokens


#  model='gpt-3.5-turbo-1106'

root = 'C:\\Users\\jthra\\Documents\\data\\CASI'
# experiment = 'feedback'
# prompt_tokens, completion_tokens = run_experiment(os.path.join(root, 'medication_status_test.csv'), 
#                                                   os.path.join(root, f'4/4_responses_{experiment}.csv'), -1, 
#                                                   experiment=experiment)

# input_fee = 0.01  # per 1k tokens
# output_fee = 0.03 # per 1k tokens

# input_cost = (prompt_tokens / 1000) * input_fee
# output_cost = (completion_tokens / 1000) * output_fee
# total_cost = (input_cost + output_cost)

# print(f'Input tokens used: {prompt_tokens}')
# print(f'Output tokens used: {completion_tokens}')
# print(f'Total fee: ${total_cost}')

f1 = score(os.path.join(root, '4/4_responses_feedback.csv'), experiment='single')


# df = pd.read_csv(os.path.join(root, 'responses_feedback.csv'))
# for i, row in df.iterrows():
#     B = row.response.split('LIST B')[-1]
#     print(B)

