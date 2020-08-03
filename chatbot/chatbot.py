from chatbot.data import Data
from chatbot.responder import PatternResponder
import os

class Chatbot:
    def __init__(self):
        self.data = Data()

    def response(self, text):
        responder = PatternResponder()
        return responder.response(text)

    def study(self):
        path = 'chatbot/textdata/'
        files = os.listdir(path)
        files_file = [f for f in files if os.path.isfile(os.path.join(path, f))]
        for file in files_file:
            with open('chatbot/textdata/' + file, 'r') as f:
                l_strip = [s.strip() for s in f.readlines()]
                for s_line in l_strip:
                    self.data.study(s_line, Data.analyze(s_line))
        self.data.save()
