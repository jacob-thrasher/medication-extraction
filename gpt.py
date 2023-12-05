from openai import OpenAI
import json
import os
import pandas as pd

def single_call(client, note, model='gpt-4-1106-preview'):
    prompt = f'Prompt: From the following discharge summary, extract all active and discontinued medicine. \
        Discharge summary: {note}'

    response = client.chat.completions.create(
        model=model,
        response_format={'type': 'json_object'},
        messages=[
            {'role': 'system', 'content': 'You are a medical information extraction assistant. Your job is to extract medicine information in JSON format'},
            {'role': 'user', 'content': prompt},
        ]
    )

    content = response.choices[0].message.content
    prompt_tokens = int(response.usage.prompt_tokens)
    completion_tokens = int(response.usage.completion_tokens)

    return content, prompt_tokens, completion_tokens




def self_feedback(client, note, model='gpt-4-1106-preview'):
    prompt = f'Prompt: From the following discharge summary, extract all active and discontinued medicine. Additionally, provide a justification for each choice \
    Discharge summary: {note}'

    response = client.chat.completions.create(
        model=model,
        response_format={'type': 'json_object'},
        messages=[
            {'role': 'system', 'content': 'You are a medical information extraction assistant. Your job is to extract medicine information in JSON format'},
            {'role': 'user', 'content': prompt},
            {'role': 'user', 'content': 'Based on your response, go back and search for any ACTIVE medications you may have missed. Again, provide justifications for each'},
            {'role': 'user', 'content': 'Based on your response, go back and search for any DISCONTINUED medications you may have missed. Again, provide justifications for each'},
            {'role': 'user', 'content': 'Double check each medication from your response and remove any incorrect choices based on the original discharge summary and your justifications. The should only contain all active and discontinued medications'}
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
        snippet = row.snippet
        index = row['index']

        if experiment == 'single': 
            response, p_tokens, c_tokens = single_call(client, snippet, model=model)
        elif experiment == 'feedback':
            response = self_feedback(client, snippet, model=model)

        print(f'Trial {i}/{num_trials}:')
        print(f'---> Input tokens used : {p_tokens}')
        print(f'---> Output tokens used: {c_tokens}')
        
        prompt_tokens += p_tokens
        completion_tokens += c_tokens

        df.loc[df['index']==index, 'response'] = response 
    
    df.to_csv(outpath)
    return prompt_tokens, completion_tokens

def resolver(csvpath):
    df = pd.read_csv()

# experiment = 'single'
# root = 'D:\\Big_Data'
# prompt_tokens, completion_tokens = run_experiment(os.path.join(root, 'medication_status_test_reduced.csv'), 
#                                                   os.path.join(root, f'responses_{experiment}_2.csv'), -1, experiment=experiment)

# input_fee = 0.01  # per 1k tokens
# output_fee = 0.03 # per 1k tokens

# input_cost = (prompt_tokens / 1000) * input_fee
# output_cost = (completion_tokens / 1000) * output_fee
# total_cost = (input_cost + output_cost)

# print(f'Input tokens used: {prompt_tokens}')
# print(f'Output tokens used: {completion_tokens}')
# print(f'Total fee: ${total_cost}')