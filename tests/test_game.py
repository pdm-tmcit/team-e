# coding:utf-8
import csv
from termcolor import colored
from game.state import WareWolfGame
from unittest import TestCase


class TestGame(TestCase):

    def test_game(self):
        file_path = "./log/village_g10.csv"
        # ログファイル読み込み
        try:
            with open(file_path) as f:
                reader = csv.reader(f)
                log_data = [row_data for row_data in reader]
        except Exception:
            print(colored("ファイルが存在しません。", "red"))
            exit()

        warewolf_game = WareWolfGame(log_data, {"test_mode": True})
        if not warewolf_game.load_prologue():
            print(colored("プロローグからプレイヤーを取得できませんでした。", "red"))
            exit()

        is_not_end = True
        last_day = 0
        while is_not_end:
            print(f"{last_day + 1}日目")
            is_not_end = warewolf_game.next_day()
            last_day += 1
            print("\n\n")

        warewolf_game.print_state()
