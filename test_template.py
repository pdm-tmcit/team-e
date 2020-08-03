# coding:utf-8
from unittest import TestCase, main
from template.template import TemplateResponder


class TestTemplate(TestCase):

    def test_template(self):
        test_patterns = [
            ("co", None, None),
            ("seer", None, None),
            ("seer", "パメラ", "白"),
            ("seer", "パメラ", "黒"),
            ("medium", None, None),
            ("medium", "パメラ", "白"),
            ("medium", "パメラ", "黒")
        ]
        responder = TemplateResponder()
        for mode, target_name, team_name in test_patterns:
            with self.subTest(mode=mode, target_name=target_name, team_name=team_name):
                print(f"入力：({mode}, {target_name}, {team_name})")
                response = responder.response(mode, target_name, team_name)
                print(f"出力：{response}\n")
                self.assertIsNotNone(response)


if __name__ == "__main__":
    main()
