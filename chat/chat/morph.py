import re
import spacy

nlp = spacy.load('ja_ginza')

def analyze(text):
    return [(t.orth_,t.tag_) for t in nlp(text)]

def is_keyword(part):
    """品詞partが学習すべきキーワードであるかどうかを真偽値で返す。"""
    return bool(re.match(r'名詞-(一般|普通名詞|固有名詞)', part))
