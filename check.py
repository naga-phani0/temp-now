import os
import re
import sys
import glob

restrict = ['selenium', 'threshold']
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

for i in glob.iglob('*.py'):
    print('started', i)
    with open(i, 'r') as file:

        for word in file.read().split():
            word_=word.lower()

            if word_ in restrict:
                print(word, 'found in file', i)
                sys.exit(1)

            if re.match(regex, word_):
                print(word, 'found in file', i)
                sys.exit(1)
            # else:
            #     print(word)
            #     print("Invalid Email")


sys.exit(0)