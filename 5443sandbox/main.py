# coding:utf-8

import sys
import csv
import re
from pprint import pprint
from termcolor import colored
import game

if __name__ == "__main__":
    # ファイル指定ない終了
    if len(argv := sys.argv) == 1:
        print(colored("ファイルを指定してください。", "red"))
        exit()

    # ログファイル読み込み
    try:
        with open(argv[1]) as f:
            reader = csv.reader(f)
            log_data = [row_data for row_data in reader]
    except Exception as e:
        print(colored("ファイルを開ませんでした。", "red"))
        exit()

    # プロローグ読み込み
    prologue_count = 0
    character_count = 0
    characters = {}
    for row_index, row_data in enumerate(log_data):
        if row_data[0] != "プロローグ":
            break

        if len(argv) == 2 or len(argv) >= 2 and int(argv[2]) == 0:
            if "=" in row_data[3] or "RP" in row_data[3]:
                print(row_index, row_data[3])
        if row_data[1] not in characters:
            characters[row_data[1]] = {}
            characters[row_data[1]][0] = row_data[2]
            characters[row_data[1]]["not_role"] = set()
            character_count += 1
        prologue_count += 1

    # 日付指定ない場合終了
    if len(argv) == 2:
        exit()

    # 発言抜き取り
    role_names_list = [[role.get("name"), role.get("one_char")] for role in game.role_data]
    important_comments = []
    for row_index, row_data in enumerate(log_data[prologue_count:]):
        if comments := re.findall("【((?!>>\d|\d{2}:\d{2}).+?)】", row_data[3]):
            important_comments.append({
                "name": row_data[1],
                "comments": comments
            })
            for comment in comments:
                if "確認" in comment:
                    # print(row_index, comment)
                    continue
                for i, role_names in enumerate(role_names_list):
                    flag = False
                    if (not_role := "非" in comment) or "CO" in comment.upper() or "対抗" in comment:
                        say_role = re.sub("[^一-龥]", "", comment)
                        # print(comment)
                        for one_char_role in [*say_role]:
                            if one_char_role in role_names:
                                flag = True
                                break
                    elif comment == role_names[0]:
                        flag = True
                    if flag:
                        if not not_role and not characters[row_data[1]].get("role"):
                            characters[row_data[1]]["role"] = game.role_data[i]["name"]
                            break
                        else:
                            characters[row_data[1]]["not_role"].add(game.role_data[i]["name"])
            if row_data[0] == f"{int(argv[2])}日目":
                if not characters[row_data[1]].get("role"):
                    color = "grey"
                elif row_data[2] == characters[row_data[1]].get("role"):
                    color = "green"
                else:
                    color = "red"
                colored_name = colored(row_data[1], color)
                print(row_index + prologue_count + 1, colored_name, row_data[2], characters[row_data[1]].get("role"), comments)

    # pprint(characters)
