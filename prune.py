

class Prune:
    def __init__(self):
        P_1 = '''
        Potential Medications:
        - "dapsone"
        - "Bactrim"
        - "6 MP"

        Non-medications:
        - "None"
        '''

        P_2 = '''
        Potential Medications:
        - "Percocet"
        - "Gemzar"
        - "Accu-Chek"
        - "Fever"

        Non-medications:
        - "Accu-Chek"
        - "Fever"
        '''

        P_3 = '''
        Potential Medications:
        - "Timentin" 
        - "vancomycin"
        - "IV"
        - "sliding scale"

        Non-medications:
        - "IV"
        - "sliding scale"
        '''

        self.prompts = [P_1, P_2, P_3]
    
    def build_prompt(self, n_shots, snippit, bulleted_list):
        final_prompt = '''Return each element in the Potential Medications list which is not clearly a specific medication name.
        Examples of elements which are not medication names are symptoms or procedures, such as "Infection", "Fever", "Biopsy", "Protocol", "Accu-Cheks", "I.V. Fluids", "Inhaler", or "Hypertension".
        If no non-verified medications are found, return "None".'''

        for i in range(n_shots):
            final_prompt += self.prompts[i]

        final_prompt += f'''
        Snippit: 
        ------------
        {snippit}'''

        return final_prompt