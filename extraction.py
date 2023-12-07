

class Extraction:
    def __init__(self):

        P_1 = '''
        Patient note:
        ------------
        She also had no clear resection of her Crohn's disease. 4. Hypertension. 5. Breast reduction in 1998. MEDICATIONS: At the time of admission include: 1. 6 MP. 2. Lisinopril. 3. Birth control pill. 4. Hydrochlorothiazide. 5. B-12. 6. Percocet. 7. Dilaudid. ALLERGIES: She has an allergy to morphine, sulfa and an adverse reaction to Remicade.

        Extracted Medications
        ------------
        - 6 MP (active)
        - Hydrochlorothiazide (active)
        - Dilaudid (active)
        - Percocet (active)
        - B-12 (active)
        - Lisinopril (active)
        - sulfa (neither)
        - Remicade (neither)
        - morphine (neither)

        '''
        
        P_2 = '''
        Patient note:
        ------------
        On hospital day number three she was weaned off her PCA and started on a fentanyl patch 75 micrograms along with Percocet for breakthrough pain which was then switched to OxyContin IR as needed for breakthrough pain. She received her Gemzar chemotherapy on _%#MMDD2003#%_ without difficulty. On hospital day number four she is stable and ready to be discharged to home with much improved pain control on her combination of fentanyl patch and oral OxyContin IR.

        Extracted Medications
        ------------
        - fentanyl (active)
        - OxyContin IR (active)
        - Gemzar (active)
        - Percocet (discontinued)
        '''

        P_3 = '''
        Patient note:
        ------------
        The patient was transferred up to the floor, aspirated, and developed a pneumonia in her right lower and middle lobes. This was treated with a course of Timentin and started on a course of vancomycin. Sputum cultures did come back with MSSA and MRSA. The patient did complete a course of Timentin. This was discontinued. The patient had a positive sputum culture for MRSA on _%#MMDD2006#%_, and the vancomycin was continued.

        Extracted Medications
        ------------
        - vancomycin (active)
        - Timentin (discontinued)
        '''

        P_4 = '''
        Patient note:
        ------------
        5. Prozac 60 mg daily by mouth. 6. Regular insulin sliding scale as follows: 150 to 200 3 units, 201 to 250 6 units, 251 to 300 8 units, 301 to 351 10 units, 351 to 400 12 units, greater than 400 call the M.D. or NP. 7. Lantus insulin 6 units q.p.m. now being given at 1800. 8. Zosyn 3.375 gm IV q.6 h. which we will continue through the _%#DD#%_ then discontinue.

        Extracted Medications
        ------------
        - Zosyn (active)
        - Lantus insulin (active)
        - Prozac (active)
        - insulin (active)
        '''

        P_5 = '''
        Patient note:
        ------------
        _%#NAME#%_ tolerated his chemotherapy well with minimal nausea and no emesis. At the time of discharge, he was in no apparent distress and was afebrile. He went home with daily doses of 6 MP which they plan to crush, at home, to help swallowing. Also at the time of his discharge he was switched from dapsone to Bactrim, which was also to be crushed and mixed in with his food for PCP prophylaxis.

        Extracted Medications
        ------------
        - 6 MP (active)
        - Bacrtim (active)
        - dapsone (discontinued)
        '''

        self.prompts = [P_1, P_2, P_3, P_4, P_5]


    def build_prompt(self, n_shots, snippit):
        
        final_prompt = f'''Return a bulleted list of all medications mentioned in the clinical snippit below. Include the medication status as a single word: "active", "discontinued", or "neither". '''

        if n_shots == 0:
            final_prompt += '''Use the following format:

            - Medication_1 (status)
            - Medication_2 (status)
            - Medication_3 (status)'''

        else:
            for i in range(n_shots):
                final_prompt += f'''
                EXAMPLE:
                {self.prompts[i]}        
                '''

        final_prompt += f'''
        Patient note: 
        ------------
        {snippit}

        Extracted Medications
        ------------
        '''
    
        return final_prompt