from bardapi import Bard

with open('token.txt', 'r') as f:
    token = f.read()

bard = Bard(token=token)
output = bard.get_answer('Hello, how are you doing?')['content']

print(output)