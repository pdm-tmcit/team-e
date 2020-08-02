# coding:utf-8
import sys
import csv
from termcolor import colored
from game.state import WareWolfGame
from unittest import TestCase, main


class TestGame(TestCase):

    def test_game(self):
        file_path = "./log/test.csv"
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


if __name__ == "__main__":
    main()
