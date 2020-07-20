import re
import spacy
import os
from pathlib import Path
from collections import defaultdict
import functools
from markov import Markov
from util import format_error
import morph

class Dictionary:
    nlp = spacy.load('ja_ginza')

    DICT_DIR = os.path.join('/mnt','c','Users','shun','Desktop',  'chat')
    DICT = {'random': 'dics/random.txt',
            'pattern': 'dics/pattern.txt',
            'template': 'dics/template.txt',
            'markov': 'dics/markov.dat',
            }

    def __init__(self):
        Dictionary.touch_dics()
        self._random = Dictionary.load_random(Dictionary.DICT['random'])
        self._pattern = Dictionary.load_pattern(Dictionary.DICT['pattern'])
        self._template = Dictionary.load_template(Dictionary.DICT['template'])
        self._markov = Dictionary.load_markov(Dictionary.DICT['markov'])

    @staticmethod
    def load_random(filename):
        """filenameをランダム辞書として読み込み、リストを返す"""
        try:
            with open(filename, encoding='utf-8') as f:
                return [l for l in f.read().splitlines() if l]
        except IOError as e:
            print(format_error(e))
            return ['こんにちは']

    @staticmethod
    def load_pattern(filename):
        """filenameをパターン辞書として読み込み、リストを返す"""
        try:
            with open(filename, encoding='utf-8') as f:
                return [Dictionary.make_pattern(l) for l
                        in f.read().splitlines() if l]
        except IOError as e:
            print(format_error(e))
            return []

    @staticmethod
    def load_template(filename):
        """filenameをテンプレート辞書として読み込み、ハッシュを返す"""
        templates = defaultdict(lambda: [])
        try:
            with open(filename, encoding='utf-8') as f:
                for line in f:
                    count, template = line.strip().split('\t')
                    if count and template:
                        count = int(count)
                        templates[count].append(template)
            return templates
        except IOError as e:
            print(format_error(e))
            return templates

    @staticmethod
    def load_markov(filename):
        """Markovオブジェクトを生成し、filenameから読み込みを行う。"""
        markov = Markov()
        try:
            markov.load(filename)
        except IOError as e:
            print(format_error(e))
        return markov

    @staticmethod
    def touch_dics():
        """辞書ファイルがなければ空のファイルを作成し、あれば何もしない。"""
        for dic in Dictionary.DICT.values():
            if not os.path.exists(dic):
                open(dic, 'w').close()

    @staticmethod
    def make_pattern(line):
        """文字列lineを\tで分割し、{'pattern': [0], 'phrases': [1]}の形式で返す。"""
        pattern, phrases = line.split('\t')
        if pattern and phrases:
            return {'pattern': pattern, 'phrases': phrases.split('|')}

    @property
    def random(self):
        return self._random

    @property
    def pattern(self):
        return self._pattern

    @property
    def template(self):
        """テンプレート辞書"""
        return self._template

    @property
    def markov(self):
        """マルコフ辞書"""
        return self._markov

    def study(self, text, parts):
        self.study_random(text)
        self.study_pattern(text, Dictionary.analyze(text))
        self.study_template(parts)
        self.study_markov(parts)

    def study_random(self, text):
        if not text in self._random:
            self._random.append(text)

    def study_pattern(self, text, parts):
        for word, part in parts:
            if self.is_keyword(part):
                duplicated = next((p for p in self._pattern if p['pattern'] == word), None)
                if duplicated:
                    if not text in duplicated['phrases']:
                        duplicated['phrases'].append(text)
                else:
                    self._pattern.append({'pattern': word, 'phrases': [text]})

    def study_template(self, parts):
        """形態素のリストpartsを受け取り、
        名詞のみ'%noun%'に変更した文字列templateをself._templateに追加する。
        名詞が存在しなかった場合、または同じtemplateが存在する場合は何もしない。
        """
        template = ''
        count = 0
        for word, part in parts:
            if morph.is_keyword(part):
                word = '%noun%'
                count += 1
            template += word

        if count > 0 and template not in self._template[count]:
            self._template[count].append(template)

    def save(self):
        """メモリ上の辞書をファイルに保存する。"""
        dic_markov = os.path.join(Dictionary.DICT_DIR, Dictionary.DICT['markov'])
        self._save_random()
        self._save_pattern()
        self._save_template()
        self._markov.save(dic_markov)

    def save_dictionary(dict_key):
        """
        辞書を保存するためのファイルを開くデコレータ。
        dict_key - Dictionary.DICTのキー。
        """
        def _save_dictionary(func):
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                """辞書ファイルを開き、デコレートされた関数を実行する。
                ディレクトリが存在しない場合は新たに作成する。"""
                if not os.path.isdir(Dictionary.DICT_DIR):
                    os.makedirs(Dictionary.DICT_DIR)
                dicfile = Dictionary.dicfile(dict_key)
                with open(dicfile, 'w', encoding='utf-8') as f:
                    result = func(self, *args, **kwargs)
                    f.write(result)
                return result
            return wrapper
        return _save_dictionary

    @save_dictionary('template')
    def _save_template(self):
        """テンプレート辞書を保存する。"""
        lines = []
        for count, templates in self._template.items():
            for template in templates:
                lines.append('{}\t{}'.format(count, template))
        return '\n'.join(lines)

    @save_dictionary('pattern')
    def _save_pattern(self):
        """パターン辞書を保存する。"""
        lines = [Dictionary.pattern2line(p) for p in self._pattern]
        return '\n'.join(lines)

    @save_dictionary('random')
    def _save_random(self):
        """ランダム辞書を保存する。"""
        return '\n'.join(self.random)

    def _find_duplicated_pattern(self, word):
        """パターン辞書に名詞wordがあればパターンハッシュを、無ければNoneを返す。"""
        return next((p for p in self._pattern if p['pattern'] == word), None)

    def load_dictionary(dict_key):
        """辞書ファイルを読み込むためのデコレータ"""
        def _load_dictionary(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                """ファイルを読み込み、行ごとに分割して関数に渡す"""
                dicfile = os.path.join(Dictionary.DICT_DIR, Dictionary.DICT[dict_key])
                if not os.path.exists(dicfile):
                    return func([], *args, **kwargs)
                with open(dicfile, encoding='utf-8') as f:
                    return func(f.read().splitlines(), *args, **kwargs)
            return wrapper
        return _load_dictionary

    def study_markov(self, parts):
        """形態素のリストpartsを受け取り、マルコフ辞書に学習させる。"""
        self._markov.add_sentence(parts)

    @staticmethod
    def analyze(text):
        return [(t.orth_,t.tag_) for t in Dictionary.nlp(text)]

    @staticmethod
    def pattern_to_line(pattern):
        """パターンのハッシュを文字列に変換する。"""
        return '{}\t{}'.format(pattern['pattern'], '|'.join(pattern['phrases']))

    @staticmethod
    def is_keyword(part):
        """品詞partが学習すべきキーワードであるかどうかを真偽値で返す。"""
        return bool(re.match(r'名詞-(一般|普通名詞)', part))

    @staticmethod
    def dicfile(key):
        """辞書ファイルのパスを 'DICT_DIR/DICT[key]' の形式で返す。"""
        return os.path.join(Dictionary.DICT_DIR, Dictionary.DICT[key])

    @staticmethod
    def pattern2line(pattern):
        """
        パターンのハッシュを文字列に変換する。
        >>> pattern = {'pattern': 'Pattern', 'phrases': ['phrases', 'list']}
        >>> Dictionary.pattern2line(pattern)
        'Pattern\\tphrases|list'
        """
        return '{}\t{}'.format(pattern['pattern'], '|'.join(pattern['phrases']))

    @staticmethod
    def line2pattern(line):
        """
        文字列lineを\tで分割し、{'pattern': [0], 'phrases': [1]}の形式で返す。
        [1]はさらに`|`で分割し、文字列のリストとする。
        >>> line = 'Pattern\\tphrases|list'
        >>> Dictionary.line2pattern(line)
        {'pattern': 'Pattern', 'phrases': ['phrases', 'list']}
        """
        pattern, phrases = line.split('\t')
        if pattern and phrases:
            return {'pattern': pattern, 'phrases': phrases.split('|')}
