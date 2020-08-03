import re
from random import choice

class PatternResponder:
        def __init__(self):
            self._pattern = []
            with open('chatbot/dics/pattern.txt', 'r') as f:
                l_strip = [s.strip() for s in f.readlines()]
                for s_line in l_strip:
                    split_line = s_line.split('	')
                    split_phrase = split_line[1].split('|')
                    self._pattern.append({'pattern': split_line[0], 'phrases':split_phrase})

            self._random = []
            with open('chatbot/dics/random.txt', 'r') as f:
                self._random = [s.strip() for s in f.readlines()]

        def response(self, text):
            for ptn in self._pattern:
                matcher = re.match(ptn['pattern'], text)
                if matcher:
                    chosen_response = choice(ptn['phrases'])
                    return chosen_response.replace('%match%', matcher[0])
            return choice(self._random)
