# coding:utf-8
import sys
import csv
import re
import spacy
from pprint import pprint
from termcolor import colored
import game


# 名詞を取得する関数
def get_nouns(sentence):
    doc = nlp(sentence)
    nouns = {
        "root": "",
        "else": set()
    }
    # 名詞取得
    for chunk in doc.noun_chunks:
        if chunk.root.dep_ not in ["compound", "appos"]:
            if chunk.root.dep_ == "ROOT":
                nouns["root"] = chunk.text
            else:
                nouns["else"].add(chunk.text)
    # ターゲットを取得できなかったら人物名の解析を行う
    if not nouns["else"]:
        json_doc = doc.to_json()
        if len(json_doc["ents"]):
            ent = json_doc["ents"][0]
            if ent["label"] == "Person":
                nouns["else"].add(doc[ent["start"]].text)
            for token in json_doc["tokens"]:
                if token["dep"] == "ROOT":
                    nouns["root"] = doc[token["head"]].text
    return nouns


# 否定が含まれるか取得する関数
def get_is_negative(sentence):
    # GiNZA使えれば使うけどわからん
    return re.search("ない|なかった|せん", sentence)


# 省略された名前からフルネームを返す関数
def get_full_player_name(short_name, players_list):
    for player_names in players_list:
        if short_name in player_names:
            return player_names[0]
    return None


# 省略された役職から正式名称を返す関数
def get_full_role_name(short_name, roles_list):
    for role_names in roles_list:
        if short_name in role_names:
            return role_names[0]
    return None

if __name__ == "__main__":
    nlp = spacy.load("ja_ginza")

    # ファイル指定されていない場合終了
    if len(argv := sys.argv) == 1:
        print(colored("ファイルを指定してください。", "red"))
        exit()

    # ログファイル読み込み
    try:
        with open(argv[1]) as f:
            reader = csv.reader(f)
            log_data = [row_data for row_data in reader]
    except Exception as e:
        print(colored("ファイルが存在しません。", "red"))
        exit()

    # プロローグ読み込み
    prologue_count = 0
    players_co_dict = {}
    joined_players_list = []
    for row_index, row_data in enumerate(log_data):
        if row_data[0] != "プロローグ":
            break
        if len(argv) > 2 and int(argv[2]) == 0:
            # プロローグ中に抜けた人がいるか
            if row_data[1] == "楽天家ゲルト" and (target := re.findall("急用により(.+?)は旅立ったよ", row_data[3])) and (player_name := get_full_player_name(target, joined_players_list)):
                players_co_dict.pop(player_name)
            # RPっぽいか
            if re.search("=|＝|rp", row_data[3].lower()):
                # わかったところでどうにもならん...
                print(row_index, row_data[3])
        if row_data[1] not in players_co_dict:
            players_co_dict[row_data[1]] = {
                0: row_data[2],
                "not_role": set()
            }
            joined_players_list.append([row_data[1], *game.all_players_dict[row_data[1]]])
        prologue_count += 1
    players_count = len(players_co_dict)

    # プロローグのみなら終了
    if len(argv) > 2 and int(argv[2]) == 0:
        exit()

    # 発言解析
    day = 0
    first_persons_list = game.first_persons_list
    roles_list = game.roles_list
    role_names_list = [role_name for role_names in roles_list for role_name in role_names]  # [役職名1, 略称1, 役職名2, 略称2, ...]
    player_names_list = [player_name for player_names in joined_players_list for player_name in player_names]  # [名前1, 略称1, 名前2, 略称2, ...]
    nouns_list = [*first_persons_list, *role_names_list, *player_names_list]  # [*一人称, *役職名, *名前]
    nouns_pattern = "|".join(nouns_list)  # 正規表現用パターン
    # ログの走査
    for row_index, row_data in enumerate(log_data[prologue_count:]):
        # 日付表示
        if len(argv) == 2 and day != re.sub("[^0-9]", "", row_data[0]):
            day = re.sub("[^0-9]", "", row_data[0])
            print(f"\n{day}日目")
        # 【】で括られた文章の抜き取り
        if not (sentences := re.findall("【((?!>>\d|\d{2}:\d{2}).+?)】", row_data[3])):
            continue
        for sentence in sentences:
            # 解析できない文章の除外
            if not re.search(nouns_pattern, sentence) or re.search("募", sentence):
                continue
            # 投票？
            if re.search("●|○|▼|▽", sentence):
                continue
            # 確認等に使えるか
            if re.search("確認|了解|ok|ｏｋ|→", sentence.lower()):
                # 結果の確認に使えるがとりあえず保留
                continue
            # 正規表現で解析するか（COのみ）
            if (not_role := "非" in sentence) or "CO" in sentence.upper() or "対抗" in sentence:
                format_sentence = re.sub("[^一-龥]", "", sentence)  # 漢字以外を削除
                is_updated_role = False
                for role_names in roles_list:
                    # 一文字ずつ役職名と一致するか確認
                    for one_char in format_sentence:
                        if one_char in role_names:
                            # 否定しているか
                            if not_role:
                                players_co_dict[row_data[1]]["not_role"].add(role_names[0])
                                is_true_sentence = row_data[2] != role_names[0]
                            else:
                                players_co_dict[row_data[1]]["role"] = role_names[0]
                                is_true_sentence = row_data[2] == role_names[0]
                                is_updated_role = True
                            if len(argv) == 2 or row_data[0] == f"{int(argv[2])}日目":
                                color = "green" if is_true_sentence else "red"
                                colored_text = colored(f"RE：\tCO {row_index + prologue_count + 1} {row_data[1]} {'≠' if not_role else '='} {role_names[0]}", color)
                                print(colored_text)
                            # 役職が更新された場合に終了
                            if is_updated_role:
                                break
                    else:
                        continue
                    break
                continue
            # GiNZAで解析（CO、占霊結果）
            nouns = get_nouns(sentence)
            # 取得した名詞のどちらかがが名詞リストに一致するか
            if len(nouns["else"]) > 2 or not nouns["else"] or not ((target := list(nouns["else"])[0]) in nouns_list or nouns["root"] in nouns_list):
                continue
            # ROOTに役職名が含まれない場合
            if nouns["root"] not in role_names_list:
                # RPの可能性あり
                if (player_name := get_full_player_name(target, joined_players_list)) and (role := players_co_dict[row_data[1]].get("role")) in ["占い師", "霊能者"]:
                    # 占霊結果が出たことにする（ROOTが白や黒以外の場合に状態更新は行わない）
                    print(f"GiNZA：\t{role} {row_index + prologue_count + 1} {player_name} {nouns['root']}")
                    print(sentence + "\n")
                continue
            role_name = get_full_role_name(nouns["root"], roles_list)
            # 一人称が含まれるか
            if target in first_persons_list:
                # 否定しているか
                if is_negative := get_is_negative(sentence):
                    players_co_dict[row_data[1]]["not_role"].add(role_name)
                    is_true_sentence = row_data[2] != role_name
                else:
                    players_co_dict[row_data[1]]["role"] = role_name
                    is_true_sentence = row_data[2] == role_name
                if len(argv) == 2 or row_data[0] == f"{int(argv[2])}日目":
                    color = "green" if is_true_sentence else "red"
                    colored_text = colored(f"GiNZA：\tCO {row_index + prologue_count + 1} {row_data[1]} {'≠' if is_negative else '='} {role_name}", color)
                    print(colored_text)
            elif talker_role := players_co_dict[row_data[1]].get("role"):  # 発言者がCOしているか
                if player_name := get_full_player_name(target, joined_players_list):
                    if len(argv) == 2 or row_data[0] == f"{int(argv[2])}日目":
                        color = "green" if row_data[2] == players_co_dict[row_data[1]].get("role") else "red"
                        colored_text = colored(f"GiNZA：\t{talker_role} {row_index + prologue_count + 1} {player_name} {'≠' if get_is_negative(sentence) else '='} {role_name}", color)
                        print(colored_text)
                        # print(sentence + "\n")
            continue
        if len(argv) == 2 or row_data[0] == f"{int(argv[2])}日目":
            if not players_co_dict[row_data[1]].get("role"):
                color = "grey"
            elif row_data[2] == players_co_dict[row_data[1]].get("role"):
                color = "green"
            else:
                color = "red"
            colored_name = colored(row_data[1], color)
            # print(row_index + prologue_count + 1, colored_name, row_data[2], players_co_dict[row_data[1]].get("role"), sentences)

    # pprint(players_co_dict)
