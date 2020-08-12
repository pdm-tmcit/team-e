from chatbot.data import Data
from chatbot.responder import PatternResponder
import os

class Chatbot:
    def __init__(self):
        self.data = Data()

    #入力されたテキストに対してresponderを呼び出し対応する返答をリターンする
    def response(self, text):
        responder = PatternResponder()
        return responder.response(text)

    # textdataディレクトリ内にあるファイルからパターンを学習
    def study(self):
        path = 'chatbot/textdata/'
        # textdataディレクトリ内にあるファイルを取得
        files = os.listdir(path)
        files_file = [f for f in files if os.path.isfile(os.path.join(path, f))]
        # テキストファイルから1行ずつ学習用関数に入れる
        for file in files_file:
            with open('chatbot/textdata/' + file, 'r') as f:
                l_strip = [s.strip() for s in f.readlines()]
                for s_line in l_strip:
                    self.data.study(s_line, Data.analyze(s_line))
        # 学習した内容を保存する
        self.data.save()
