import os
import re
import spacy

class Data:
    nlp = spacy.load('ja_ginza')

    def __init__(self):
        # 辞書ファイルが無ければ作成する
        if not os.path.exists('chatbot/dics/pattern.txt'):
            open('chatbot/dics/pattern.txt', 'w').close()
        # 現時点である辞書ファイルの読み込み
        self._pattern = []
        with open('chatbot/dics/pattern.txt', 'r') as f:
            l_strip = [s.strip() for s in f.readlines()]
            for s_line in l_strip:
                split_line = s_line.split('	')
                self._pattern.append({'pattern': split_line[0], 'phrases':[split_line[1]]})

    # 言語解析を行い単語と品詞のセットを返す
    def analyze(text):
        nlp = spacy.load('ja_ginza')
        return [(t.orth_, t.tag_) for t in nlp(text)]

    # 単語が名詞であるかどうかの判別
    def decision_noun(part):
        return bool(re.match(r'名詞-(一般|普通名詞)', part))

    # 学習を行う関数
    def study(self, text, parts):
        for word, part in parts:
            if Data.decision_noun(part):
                # 今まで学習したパターンがあるならそこに追加・なければ新規作成をしている
                duplicated = next((p for p in self._pattern if p['pattern'] == word), None)
                if duplicated:
                    if not text in duplicated['phrases']:
                        duplicated['phrases'].append(text)
                else:
                    self._pattern.append({'pattern': word, 'phrases': [text]})

    # 学習した内容をファイルに書き込みしている
    def save(self):
        with open('chatbot/dics/pattern.txt', mode='w', encoding='utf-8') as f:
            f.write('\n'.join([Data.pattern_to_line(p) for p in self._pattern]))

    # パターンを保存用に1行に変換している
    def pattern_to_line(pattern):
        return '{}\t{}'.format(pattern['pattern'], '|'.join(pattern['phrases']))
