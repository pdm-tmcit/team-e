import os
import sys
from random import choice
from collections import defaultdict
import re
import copy
import dill
import morph
import gzip, pickle

class Markov:
    ENDMARK = '%END%'
    CHAIN_MAX = 30

    def __init__(self):
        self._dic = defaultdict(lambda: defaultdict(lambda: []))
        self._starts = defaultdict(lambda: 0)

    def add_sentence(self, parts):
        if len(parts) < 3:
            return

        parts = copy.copy(parts)
        prefix1, prefix2 = parts.pop(0)[0], parts.pop(0)[0]

        self.__add_start(prefix1)
        for suffix, _ in parts:
            self.__add_suffix(prefix1, prefix2, suffix)
            prefix1, prefix2 = prefix2, suffix
        self.__add_suffix(prefix1, prefix2, Markov.ENDMARK)

    def __add_suffix(self, prefix1, prefix2, suffix):
        self._dic[prefix1][prefix2].append(suffix)

    def __add_start(self, prefix1):
        self._starts[prefix1] += 1

    def generate(self, keyword):
        if not self._dic:
            return None

        prefix1 = keyword if self._dic[keyword] else choice(list(self._starts.keys()))
        prefix2 = choice(list(self._dic[prefix1].keys()))
        words = [prefix1, prefix2]

        for _ in range(Markov.CHAIN_MAX):
            suffix = choice(self._dic[prefix1][prefix2])
            if suffix == Markov.ENDMARK:
                break
            words.append(suffix)
            prefix1, prefix2 = prefix2, suffix

        return ''.join(words)

    def load(self, filename):
        """ファイルfilenameから辞書データを読み込む。"""
        with open(filename, 'rb') as f:
            self._dic, self._starts = dill.load(f)

    def save(self, filename):
        """ファイルfilenameへ辞書データを書き込む。"""
        with open(filename, 'wb') as f:
            dill.dump((self._dic, self._starts), f)
