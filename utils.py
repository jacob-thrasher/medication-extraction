import os
import pandas as pd
import ast

def score(csvpath, experiment='single'):
    precision = 0
    recall = 0
    f1 = 0
    df = pd.read_csv(csvpath)
    for i, row in df.iterrows():
        active_meds = ast.literal_eval(row.active_medications)
        discontinued_meds = ast.literal_eval(row.discontinued_medications)
        neither_meds = ast.literal_eval(row.neither_medications)
        ground_truth = labels_to_dict(active_meds, discontinued_meds, neither_meds)

        extracted_med, extracted_label = parse_response(row.response, experiment=experiment)

    
        f, p, r = compute_f1(extracted_med, extracted_label, ground_truth)
        f1 += f
        precision += p
        recall += r

    print('Precision:', precision / len(df))
    print('Recall:', recall / len(df))
    print('F1:', f1 / len(df))

# TODO: Improve calculation
def compute_f1(extracted_meds, extracted_labels, labels):
    TP = 0
    FP = 0
    for i in range(len(extracted_meds)):
        ext_med = extracted_meds[i]
        ext_lab = extracted_labels[i]

        try:
            if labels[ext_med] == ext_lab: TP += 1
            else: FP += 1
        except:
            FP += 1
            continue

    FN = 0
    ground_truth_meds = list(labels.keys())
    for gt_med in ground_truth_meds:
        if gt_med not in extracted_meds: FN += 1

    precision = TP / (TP + FP) 
    recall = TP / (TP + FN) if TP + FN > 0 else 0

    f1 = (2 * precision * recall) / (precision + recall) if precision + recall > 0 else 0

    return f1, precision, recall

def labels_to_dict(active_meds, discontinued_meds, neither_meds):
    # To lower (just in case)
    active_meds = [x.lower() for x in active_meds]
    discontinued_meds = [x.lower() for x in discontinued_meds]
    neither_meds = [x.lower() for x in neither_meds]


    active_lab = ['active']*len(active_meds)
    discontinued_lab = ['discontinued']*len(discontinued_meds)
    neither_lab = ['neither']*len(neither_meds)

    agg_meds = active_meds + discontinued_meds + neither_meds
    agg_lab = active_lab + discontinued_lab + neither_lab

    return dict(zip(agg_meds, agg_lab))

def parse_response(response, experiment='single'):
    '''
    Responses formatted as:

    - medication_1 (status_1)
    - medication_2 (status_2)
    - medication_3 (status_3)

    Return lists:
    [medication_1, medication_2, medication_3]
    [status_1, status_2, status_3]
    '''
    if experiment == 'feedback': response = response.split('LIST B')[-1]

    response_as_list = response.split('\n')
    medicine = []
    status = []
    for r in response_as_list:
        if r == '': continue

        r = r.split(' ')
        medicine.append((' ').join(r[1:-1]).lower())
        status.append(r[-1].strip('()').lower())

    # for i in range(len(status)):
    #     if status[i] == 'active': c = 0
    #     elif status[i] == 'discontinued': c = 1
    #     else: c = 2  

    #     status[i] = c 
    return medicine, status