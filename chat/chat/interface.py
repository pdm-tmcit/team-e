from responder import RandomResponder, WhatResponder, PatternResponder, TemplateResponder, MarkovResponder
from dictionary import Dictionary
from random import choice, randrange
import morph

class interface:
    def __init__(self, name):
        self._dictionary = Dictionary()

        self._responders = {
            'what':   WhatResponder('What', self._dictionary),
            'random': RandomResponder('Random', self._dictionary),
            'pattern': PatternResponder('Pattern', self._dictionary),
            'template': TemplateResponder('Template', self._dictionary),
            'markov': MarkovResponder('Markov', self._dictionary),
        }
        self._name = name
        self._responder = self._responders['pattern']

    def dialogue(self, text):
        chance = randrange(0, 100)
        if chance in range(0, 29):
            self._responder = self._responders['pattern']
        elif chance in range(30, 49):
            self._responder = self._responders['template']
        elif chance in range(50, 69):
            self._responder = self._responders['random']
        elif chance in range(70, 89):
            self._responder = self._responders['markov']
        else:
            self._responder = self._responders['what']

        parts = morph.analyze(text)
        response = self._responder.response(text, parts)
        self._dictionary.study(text, parts)
        return response

    def save(self):
        self._dictionary.save()

    @property
    def name(self):
        return self._name

    @property
    def responder_name(self):
        return self._responder.name
