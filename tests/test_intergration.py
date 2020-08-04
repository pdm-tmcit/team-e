# coding:utf-8
import csv
from termcolor import colored
from game.state import WareWolfGame
from unittest import TestCase


class TestIntergration(TestCase):

    def test_intergration(self):
        file_path = "./log/test.csv"
        # ログファイル読み込み
        try:
            with open(file_path) as f:
                reader = csv.reader(f)
                log_data = [row_data for row_data in reader]
        except Exception:
            print(colored("ファイルが存在しません。", "red"))
            exit()

        warewolf_game = WareWolfGame(log_data, {"logging": False})
        if not warewolf_game.load_prologue():
            print(colored("プロローグからプレイヤーを取得できませんでした。", "red"))
            exit()

        is_not_end = True
        while is_not_end:
            is_not_end = warewolf_game.next_day()

        result_path = f"./results/{file_path.split('/')[-1]}"
        with open(result_path, "w") as f:
            writer = csv.writer(f)
            writer.writerows(warewolf_game.generate_log_data)

        try:
            with open(result_path) as f:
                reader = csv.reader(f)
                generate_log_data = [row_data for row_data in reader]
        except Exception:
            print(colored("ファイルが存在しません。", "red"))
            exit()
        for row_data in generate_log_data:
            self.assertTrue(row_data[3])
