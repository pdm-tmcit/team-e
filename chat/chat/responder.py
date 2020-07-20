from random import choice
import re
import morph

class responder:
    def __init__(self, name, dictionary):
        self._name = name
        self._dictionary = dictionary

    def response(self, *args):
        pass

    @property
    def name(self):
        return self._name

class WhatResponder(responder):
    def response(self,text, _):
        return '{}ってなに？'.format(text)

class RandomResponder(responder):
    def response(self, *args):
        return choice(self._dictionary.random)

class PatternResponder(responder):
    def response(self, text, _):
        for ptn in self._dictionary.pattern:
            matcher = re.match(ptn['pattern'], text)
            if matcher:
                chosen_response = choice(ptn['phrases'])
                return chosen_response.replace('%match%', matcher[0])
        return choice(self._dictionary.random)

class TemplateResponder(responder):
    def response(self, _, parts):
        """形態素解析結果partsに基づいてテンプレートを選択・生成して返す。"""
        keywords = [word for word, part in parts if morph.is_keyword(part)]
        count = len(keywords)
        if count > 0:
            if count in self._dictionary.template:
                template = choice(self._dictionary.template[count])
                for keyword in keywords:
                    template = template.replace('%noun%', keyword, 1)
                return template
        return choice(self._dictionary.random)

class MarkovResponder(responder):
    def response(self, _, parts):
        """形態素のリストpartsからキーワードを選択し、それに基づく文章を生成して返す。
        キーワードに該当するものがなかった場合はランダム辞書から返す。"""
        keyword = next((w for w, p in parts if morph.is_keyword(p)), '')
        response = self._dictionary.markov.generate(keyword)
        return response if response else choice(self._dictionary.random)
