import random
from template import sentences


class TemplateResponder():
    SIRO = "白"
    KURO = "黒"

    def __init__(self):
        return

    # zenbu random
    def response(self, mode, target_name=None, team_name=None):
        self.mode = mode
        self.target_name = target_name
        self.team_name = team_name

        if self.mode == "co":
            return self.co()
        elif self.mode == "seer":
            return self.seer()
        elif self.mode == "medium":
            return self.medium()

        return self.random()

    def __replace_target(self, sentence):
        return sentence.replace("%target%", self.target_name)

    def __unknown(self, r):
        return r["unknown"][random.randint(0, len(r["unknown"])-1)]

    def __get_by_random(self, r):
        return r[random.randint(0, len(r)-1)]

    def co(self):
        r = sentences.co.copy()
        return self.__get_by_random(r)

    def seer(self):
        r = sentences.seer.copy()

        if self.target_name is None:
            return self.__unknown(r)

        if self.team_name == TemplateResponder.SIRO:
            return self.__replace_target(self.__get_by_random(r['siro']))

        elif self.team_name == TemplateResponder.KURO:
            return self.__replace_target(self.__get_by_random(r['kuro']))
        else:
            return self.__unknown(r)

    def medium(self):
        r = sentences.medium.copy()

        if self.target_name is None:
            return self.__unknown(r)

        if self.team_name == TemplateResponder.SIRO:
            return self.__replace_target(self.__get_by_random(r['siro']))
        elif self.team_name == TemplateResponder.KURO:
            return self.__replace_target(self.__get_by_random(r['kuro']))
        else:
            return self.__unknown(r)

    def random(self):
        r = sentences.random.copy()
        return self.__get_by_random(r)

