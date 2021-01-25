# coding:utf-8
from unittest import TestCase
from chatbot.chatbot import Chatbot


class TestChatbot(TestCase):

    def test_chatbot(self):
        test_patterns = [
            "朝ごはんは白米に味噌汁に卵焼きが鉄板なんです",
            "今年のクリスマスマーケットは誰と行こうかな",
            "あなたが落としたのは金の財布ですか、銀の財布ですか。",
            "肩がこるんですけどマッサージしてくれる人ーーー",
            "村人のひといますかー？"
        ]
        responder = Chatbot()
        for sentence in test_patterns:
            with self.subTest(sentence=sentence):
                print(f"入力：{sentence}")
                response = responder.response(sentence)
                print(f"出力：{response}\n")
                self.assertTrue(response)
