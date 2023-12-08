from openai import OpenAI
import json
import os
import pandas as pd
import ast
from utils import *
from sklearn.metrics import f1_score

from extraction import Extraction
from omission import Omission
from evidence import Evidence
from prune import Prune

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

def n_shot_verification(client, note, n_shots, model=''):
    print(f"Using {model} model")
    prompt_tokens = 0
    completion_tokens = 0

    # Initial extraction
    extraction_prompt = Extraction().build_prompt(n_shots, note)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': 'You are a medical information extraction assistant. Your job is to extract the status of medicine from clinical snippits'},
            {'role': 'user', 'content': extraction_prompt},
        ]
    )
    extraction_text = response.choices[0].message.content
    prompt_tokens += int(response.usage.prompt_tokens)
    completion_tokens += int(response.usage.completion_tokens)

    # Omission
    omission_prompt = Omission().build_prompt(n_shots, note, extraction_text)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': 'You are a medical information extraction assistant. Your job is to extract the status of medicine from clinical snippits'},
            {'role': 'user', 'content': omission_prompt},
        ]
    )
    omission_text = response.choices[0].message.content
    prompt_tokens += int(response.usage.prompt_tokens)
    completion_tokens += int(response.usage.completion_tokens)

    # Evidence
    evidence_prompt = Evidence().build_prompt(n_shots, note, omission_text)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': 'You are a medical information extraction assistant. Your job is to extract the status of medicine from clinical snippits'},
            {'role': 'user', 'content': evidence_prompt},
        ]
    )
    evidence_text = response.choices[0].message.content
    prompt_tokens += int(response.usage.prompt_tokens)
    completion_tokens += int(response.usage.completion_tokens)

    # Revise
    revise_prompt = f"""Revise the status of each medication, based on the patient note and the extracted evidence snippet. 
                    The status should be active, discontinued, or neither. If the evidence does not show that status is clearly active or discontinued, revise it to neither.
                    The output should be returned in the following format with no other text:
                    
                    - Medication_1 (status)
                    - Medication_2 (status)
                    - Medication_3 (status)

                    Patient Note:
                    ------------
                    {note}

                    Extracted Medications
                    ------------
                    {evidence_text}
                    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': 'You are a medical information extraction assistant. Your job is to extract the status of medicine from clinical snippits'},
            {'role': 'user', 'content': revise_prompt},
        ]
    )
    revise_text = response.choices[0].message.content
    prompt_tokens += int(response.usage.prompt_tokens)
    completion_tokens += int(response.usage.completion_tokens)

    # Prune
    prune_prompt = f'''Remove each element in the bulleted list which is not clearly a specific medication name.
        Examples of elements which are not medication names are symptoms or procedures, such as "Infection", "Fever", "Biopsy", "Protocol", "Accu-Cheks", "I.V. Fluids", "Inhaler", or "Hypertension".
        The output should be returned in the same form as the bulleted list with not extra text

        Bulleted list:
        {revise_text}
        '''
    response = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': 'You are a medical information extraction assistant. Your job is to extract the status of medicine from clinical snippits'},
            {'role': 'user', 'content': prune_prompt},
        ]
    )
    prune_text = response.choices[0].message.content
    prompt_tokens += int(response.usage.prompt_tokens)
    completion_tokens += int(response.usage.completion_tokens)

    all_outputs = {
        'extraction': extraction_text,
        'omission': omission_text,
        'evidence': evidence_text,
        'revise': revise_text,
        'prune': prune_text
    }
    return all_outputs, prompt_tokens, completion_tokens


def zero_shot_self_feedback(client, note, model='gpt-4-1106-preview'):
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

def run_experiment(csvpath, outpath, num_trials, experiment='single', model='', n_shot=1):
    assert experiment in ['single', 'feedback', 'SV'], f'type must be in [single, feedback], got {experiment}'

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
            response, p_tokens, c_tokens = zero_shot_self_feedback(client, snippet, model=model)
        elif experiment == 'SV':
            response, p_tokens, c_tokens = n_shot_verification(client, snippet, n_shot, model=model)

        print(f'Trial {i}/{num_trials}:')
        print(f'---> Input tokens used : {p_tokens}')
        print(f'---> Output tokens used: {c_tokens}')
        
        prompt_tokens += p_tokens
        completion_tokens += c_tokens

        if experiment in ['single', 'feedback']:
            df.loc[df['index']==index, 'response'] = response 
        else:
            df.loc[df['index']==index, 'response'] = response['prune']
            df.loc[df['index']==index, 'all_outputs'] = str(response)
    
        df.to_csv(outpath)
    return prompt_tokens, completion_tokens


#  model='gpt-3.5-turbo-1106'


root = 'D:\\Big_Data\\CASI'
experiment = 'SV'
filename = 'SV/all_2.csv'
prompt_tokens, completion_tokens = run_experiment(os.path.join(root, filename), 
                                                  os.path.join(root, filename), 25, 
                                                  experiment=experiment, n_shot=1,
                                                  model='gpt-4-1106-preview')

input_fee = 0.001  # per 1k tokens
output_fee = 0.002 # per 1k tokens

input_cost = (prompt_tokens / 1000) * input_fee
output_cost = (completion_tokens / 1000) * output_fee
total_cost = (input_cost + output_cost)

print(f'Input tokens used: {prompt_tokens}')
print(f'Output tokens used: {completion_tokens}')
print(f'Total fee: ${total_cost}')

score(os.path.join(root, filename), experiment='single')

# root = 'D:\\Big_Data\\CASI\\SV\\gpt35\\3 shot'
# f1 = score(os.path.join(root, 'all.csv'), experiment='single')
# f1 = score(os.path.join(root, 'no_prune.csv'), experiment='single')
# f1 = score(os.path.join(root, 'no_omission.csv'), experiment='single')


# df = pd.read_csv(os.path.join(root, 'responses_feedback.csv'))
# for i, row in df.iterrows():
#     B = row.response.split('LIST B')[-1]
#     print(B)

