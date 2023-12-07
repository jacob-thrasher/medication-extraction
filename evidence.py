

class Evidence:
    def __init__(self):
        P_1 = '''
        Patient note:
        ------------
        On hospital day number three she was weaned off her PCA and started on a fentanyl patch 75 micrograms along with Percocet for breakthrough pain which was then switched to OxyContin IR as needed for breakthrough pain. She received her Gemzar chemotherapy on _%#MMDD2003#%_ without difficulty. On hospital day number four she is stable and ready to be discharged to home with much improved pain control on her combination of fentanyl patch and oral OxyContin IR.

        Extracted Medications
        ------------
        - fentanyl (active)
        - OxyContin IR (active)
        - Gemzar (active)
        - Percocet (discontinued)

        Evidence
        ------------
        - "Percocet" (discontinued) "along with Percocet for breakthrough pain which was then switched to OxyContin IR"
        - "Gemzar" (active) "received her Gemzar chemotherapy on _%#MMDD2003#%_ without difficulty"
        - "OxyContin IR" (active) "along with Percocet for breakthrough pain which was then switched to OxyContin IR"
        - "fentanyl" (active) "she was weaned off her PCA and started on a fentanyl patch"
        '''

        P_2 = '''Patient Note
        ------------
        The patient was transferred up to the floor, aspirated, and developed a pneumonia in her right lower and middle lobes. This was treated with a course of Timentin and started on a course of vancomycin. Sputum cultures did come back with MSSA and MRSA. The patient did complete a course of Timentin. This was discontinued. The patient had a positive sputum culture for MRSA on _%#MMDD2006#%_, and the vancomycin was continued.

        Extracted medications
        ---------------------
        - "Timentin" (discontinued)
        - "vancomycin" (active)

        Evidence
        --------
        - "Timentin" (discontinued) "patient did complete a course of Timentin. This was discontinued"
        - "vancomycin" (active) "started on a course of vancomycin"'''

        P_3 = '''Patient Note
        ------------
        _%#NAME#%_ tolerated his chemotherapy well with minimal nausea and no emesis. At the time of discharge, he was in no apparent distress and was afebrile. He went home with daily doses of 6 MP which they plan to crush, at home, to help swallowing. Also at the time of his discharge he was switched from dapsone to Bactrim, which was also to be crushed and mixed in with his food for PCP prophylaxis.

        Extracted medications
        ---------------------
        - "dapsone" (discontinued)
        - "Bactrim" (active)
        - "fentanyl" (active)
        - "6 MP" (active)

        Evidence
        --------
        - "dapsone" (discontinued) "he was switched from dapsone to Bactrim"
        - "Bactrim" (active) "he was switched from dapsone to Bactrim"
        - "fentanyl" (active) "NO_EVIDENCE"
        - "6 MP" (active) "he went home with daily doses of 6 MP"'''

        self.prompts = [P_1, P_2, P_3]
    
    def build_prompt(self, n_shots, snippit, bulleted_list):
        final_prompt = f"""
        Find the span of text which corresponds to each extracted medication and its status. If no evidence is found, write "NO_EVIDENCE". Write a bullet for every extracted medication.
        As the output, return only the list of medications, their status, and the evidence. Do not include any other text"""

        if n_shots > 0:
            for i in range(n_shots):
                final_prompt += f'''\nEXAMPLE:
                {self.prompts[i]}
                '''

        final_prompt += f'''
        Patient Note: 
        ------------
        {snippit}

        Extracted medications
        ---------------------
        {bulleted_list}

        Evidence
        --------
        '''

        return final_prompt