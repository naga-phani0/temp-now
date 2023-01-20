import glob
import re
import sys


class Main:
    def __init__(self):

        self.must = ['requests', ' job_meta_upload_script_v2', 'class']
        self.restrict = ['selenium']
        self.regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    def file(self):
        for i in glob.iglob('*.py'):

            if i in 'check.py':
                continue

            with open(i, 'r') as file:

                for word in file.read().split():
                    word_ = word.lower().replace("\'", '')

                    if word_ in self.restrict:
                        # for finding restrict words
                        print(f'found {word_}  in file', i)
                        sys.exit(1)

                    if re.match('print.+', word_):  # for finding print
                        print(f'found {word_}  in file', i)
                        sys.exit(1)

                    elif re.match(self.regex, word_):  # match the email
                        print(f'found {word_}  in file', i)
                        sys.exit(1)

                    # elif word_ in must:
                    #     print(word_, 'found in file', i)
                    #     continue
                    # # sys.exit(0)

                print('Completed', i)

        sys.exit(0)


if __name__ == '__main__':
    obj = Main()
    obj.file()
