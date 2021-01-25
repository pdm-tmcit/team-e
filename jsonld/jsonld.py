# coding:utf-8

import json
import os
from time import gmtime, strftime
import copy


class JsonldGenerator:

    def __init__(self, filename, name, role):
        self.filename = filename
        self.name = name
        self.role = role

        self.chat_jsonld = json.load(open("jsonld/chat.jsonld", "r"))
        self.chat_jsonld["myCharacter"]["name"]["ja"] = name
        self.chat_jsonld["myCharacter"]["role"]["name"]["ja"] = role
        self.chat_jsonld["character"]["name"]["ja"] = name

        self.noon_vote_jsonld = json.load(open("jsonld/noonVote.jsonld", "r"))
        self.noon_vote_jsonld["myCharacter"]["name"]["ja"] = name
        self.noon_vote_jsonld["myCharacter"]["role"]["name"]["ja"] = role
        self.noon_vote_jsonld["character"]["name"]["ja"] = name

        self.night_vote_jsonld = json.load(open("jsonld/nightVote.jsonld", "r"))
        self.night_vote_jsonld["myCharacter"]["name"]["ja"] = name
        self.night_vote_jsonld["myCharacter"]["role"]["name"]["ja"] = role
        self.night_vote_jsonld["character"]["name"]["ja"] = name

    def chat(self, day, sentence):
        time = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
        new_jsonld = copy.deepcopy(self.chat_jsonld)
        new_jsonld["day"] = day
        new_jsonld["text"]["@value"] = sentence
        new_jsonld["phaseStartTime"] = time
        new_jsonld["serverTimestamp"] = time
        new_jsonld["clientTimestamp"] = time

        try:
            os.mkdir(f"results/{self.filename}/{day}")
        except Exception:
            return

        with open(f"results/{self.filename}/{day}/chat.jsonld", "w") as f:
            json.dump(new_jsonld, f, ensure_ascii=False, indent=4)

    def noon_vote(self, day, target_name):
        time = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
        new_jsonld = copy.deepcopy(self.noon_vote_jsonld)
        new_jsonld["day"] = day
        new_jsonld["phaseStartTime"] = time
        new_jsonld["serverTimestamp"] = time
        new_jsonld["clientTimestamp"] = time
        new_jsonld["character"]["name"]["ja"] = target_name

        try:
            with open(f"results/{self.filename}/{day}/noonVote.jsonld", "w") as f:
                json.dump(new_jsonld, f, ensure_ascii=False, indent=4)
        except Exception:
            return

    def night_vote(self, day, target_name):
        time = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
        new_jsonld = copy.deepcopy(self.night_vote_jsonld)
        new_jsonld["day"] = day
        new_jsonld["phaseStartTime"] = time
        new_jsonld["serverTimestamp"] = time
        new_jsonld["clientTimestamp"] = time
        new_jsonld["character"]["name"]["ja"] = target_name

        try:
            with open(f"results/{self.filename}/{day}/nightVote.jsonld", "w") as f:
                json.dump(new_jsonld, f, ensure_ascii=False, indent=4)
        except Exception:
            return
