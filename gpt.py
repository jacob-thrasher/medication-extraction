from openai import OpenAI
import json
import os
import pandas as pd

def single_call(client, note, model='gpt-4-1106-preview'):
    prompt = f'Prompt: From the following text note, extract all active and discontinued medicine. Text: {note}'

    response = client.chat.completions.create(
        model=model,
        response_format={'type': 'json_object'},
        messages=[
            {'role': 'system', 'content': 'You are a medical information extraction assistant. Your job is to extract medicine information in JSON format'},
            {'role': 'user', 'content': prompt},
        ]
    )


def self_feedback(client, note):
    return

def run_experiment(csvpath, outpath, num_trials, experiment='single'):
    assert experiment in ['single', 'feedback', 'test'], f'type must be in [single, feedback], got {experiment}'

    with open('key.json', 'r') as f:
        key = json.load(f)['OPENAI_API_KEY']
    client = OpenAI(api_key=key)

    df = pd.read_csv(csvpath)[:num_trials]
    for i, row in df.iterrows():
        snippet = row.snippet
        index = row['index']

        if experiment == 'single': 
            response = single_call(client, None)
        elif experiment == 'feedback':
            response = self_feedback(client, None)

        df.loc[df['index']==index, 'response'] = response 
    
    df.to_csv(outpath)

root = 'C:\\Users\\jthra\\Documents\\data\\CASI'
run_experiment(os.path.join(root, 'medication_status_test.csv'), os.path.join(root, 'est.csv'), 20, experiment='test')