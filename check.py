import os
import re
import sys
import glob

must=['requests',' job_meta_upload_script_v2','class']
restrict = ['selenium','print']
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

for i in glob.iglob('*.py'):
    print('started', i)
    with open(i, 'r') as file:

        for word in file.read().split():
            word_ = word.lower().strip("\'")

            if word_ in restrict:
                print(word_, 'found in file', i)
                sys.exit(1)

            elif re.match(regex, word_): # match the emal
                print(word, 'found in file', i)
                sys.exit(1)

            elif word_ in must:
                print(word_, 'found in file', i)
                sys.exit(0)



sys.exit(0)
