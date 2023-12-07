

class Omission:
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
        - sulfa (neither)
        - Remicade (neither)
        

        Missed Medications
        ------------
        - Percocet (active)
        - B-12 (active)
        - Lisinopril (active)
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

        Missed Medications
        ------------
        - Gemzar (active)
        - Percocet (discontinued)

        '''

        P_3 = '''
        Patient note:
        ------------
        The patient was transferred up to the floor, aspirated, and developed a pneumonia in her right lower and middle lobes. This was treated with a course of Timentin and started on a course of vancomycin. Sputum cultures did come back with MSSA and MRSA. The patient did complete a course of Timentin. This was discontinued. The patient had a positive sputum culture for MRSA on _%#MMDD2006#%_, and the vancomycin was continued.

        Extracted Medications
        ------------
        - Timentin (discontinued)

        Missed Medications
        ------------
        - vancomycin (active)
        '''

        self.prompts = [P_1, P_2, P_3]
    
    def build_prompt(self, n_shots, snippit, bulleted_list):
        final_prompt = '''
        List all medication names in the patient note that were missed in Extracted medications list. 
        If no additional medications are found, return "None".
        Return a merged list of extracted medications and missed medications in the bulleted format without any extra text.
        '''

        if n_shots > 0:
            for i in range(n_shots):
                final_prompt += f'''\nEXAMPLE
                {self.prompts[i]}
                '''

        final_prompt += f'''
        Patient note: 
        ------------
        {snippit}

        Extracted Medications
        ------------
        {bulleted_list}

        Missed Medications
        ------------
        '''

        return final_prompt