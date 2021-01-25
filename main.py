# coding:utf-8
import sys
import os
from time import gmtime, strftime
import csv
from termcolor import colored
from game.state import WareWolfGame

if __name__ == "__main__":
    # ファイル指定されていない場合終了
    if len(argv := sys.argv) == 1:
        print(colored("ファイルを指定してください。", "red"))
        exit()

    # ログファイル読み込み
    try:
        with open(argv[1]) as f:
            reader = csv.reader(f)
            log_data = [row_data for row_data in reader]
    except Exception:
        print(colored("ファイルが存在しません。", "red"))
        exit()

    filename = argv[1].split('/')[-1][0:-4]
    time = strftime("%Y%m%d%H%M%S", gmtime())
    os.mkdir(f"results/{filename}_{time}")
    warewolf_game = WareWolfGame(log_data)
    if not warewolf_game.load_prologue():
        print(colored("プロローグからプレイヤーを取得できませんでした。", "red"))
        exit()

    is_not_end = True
    last_day = 0
    while is_not_end:
        print(f"{last_day + 1}日目")
        is_not_end = warewolf_game.next_day()
        last_day += 1
        print()

    with open(f"./results/{filename}_{time}/{filename}.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(warewolf_game.generate_log_data)
