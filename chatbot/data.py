import os
import re
import spacy

class Data:
    nlp = spacy.load('ja_ginza')

    def __init__(self):
        if not os.path.exists('chatbot/dics/pattern.txt'):
            open('chatbot/dics/pattern.txt', 'w').close()
        self._pattern = []
        with open('chatbot/dics/pattern.txt', 'r') as f:
            l_strip = [s.strip() for s in f.readlines()]
            for s_line in l_strip:
                split_line = s_line.split('	')
                self._pattern.append({'pattern': split_line[0], 'phrases':[split_line[1]]})

    def analyze(text):
        nlp = spacy.load('ja_ginza')
        return [(t.orth_, t.tag_) for t in nlp(text)]

    def decision_noun(part):
        return bool(re.match(r'名詞-(一般|普通名詞)', part))

    def study(self, text, parts):
        for word, part in parts:
            if Data.decision_noun(part):
                duplicated = next((p for p in self._pattern if p['pattern'] == word), None)
                if duplicated:
                    if not text in duplicated['phrases']:
                        duplicated['phrases'].append(text)
                else:
                    self._pattern.append({'pattern': word, 'phrases': [text]})

    def save(self):
        with open('chatbot/dics/pattern.txt', mode='w', encoding='utf-8') as f:
            f.write('\n'.join([Data.pattern_to_line(p) for p in self._pattern]))

    def pattern_to_line(pattern):
        return '{}\t{}'.format(pattern['pattern'], '|'.join(pattern['phrases']))
