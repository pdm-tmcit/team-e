# coding:utf-8
import re
import spacy
from . import dictionary


class NLP:
    nlp = spacy.load('ja_ginza')

    def __init__(self):
        self.first_persons_list = dictionary.first_persons_list
        self.teams_list = dictionary.teams_list
        self.roles_list = dictionary.roles_list
        self.all_players_dict = dictionary.all_players_dict
        self._role_names_list = [role_name for role_names in self.roles_list for role_name in role_names]  # [役職名1, 略称1, 役職名2, 略称2, ...]
        self._role_names_pattern = "|".join(self._role_names_list)  # 役職名の正規表現用パターン
        self._joined_players_list = []  # [[名前1, 略称1], [名前2, 略称2], ...]
        self._nouns_list = []  # [*一人称, *役職名, *名前]
        self._nouns_pattern = "|".join(self._nouns_list)  # 主語の正規表現用パターン

    # 参加中のプレイヤー登録
    def set_joined_players(self, joined_players_list):
        player_names_list = [player_name for player_names in joined_players_list for player_name in player_names]  # [名前1, 略称1, 名前2, 略称2, ...]
        self._joined_players_list = joined_players_list
        self._nouns_list = [*self.first_persons_list, *self._role_names_list, *player_names_list]
        self._nouns_pattern = "|".join(self._nouns_list)

    # 名詞を取得する関数
    def get_nouns(self, sentence):
        doc = NLP.nlp(sentence)
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

    # 否定が含まれるか
    def get_is_negative(self, sentence):
        # GiNZA使えれば使うけどわからん
        return re.search("無い|ない|無かった|なかった|せん", sentence)

    # 省略された名前からフルネームの取得
    def get_full_player_name(self, text, joined_players_list=None):
        for player_names in (joined_players_list or self._joined_players_list):
            if text in player_names:
                return player_names[0]
        return None

    # 省略された役職から正式名称の取得
    def get_full_role_name(self, text):
        for role_names in self.roles_list:
            if text in role_names:
                return role_names[0]
        return None

    # 占霊結果から所属名の取得
    def get_team_name(self, text):
        for team_names in self.teams_list:
            if text in team_names:
                return team_names[0]
        return None

    # 文章の解析
    def parse(self, talker_dict, sentence):
        results = []
        # 確認等に使えるか1（これのみ名詞リストの名詞を含まなくていいものとする）
        if re.search("確認", lower_sentence := sentence.lower()) and not re.search("仮|決定|時刻|時間", lower_sentence):
            if re.search("co|ｃｏ|" + self._role_names_pattern, lower_sentence):
                results.append({
                    "use_engine": "RE",
                    "mode": "co_check"
                })
            else:
                results.append({
                    "use_engine": "RE",
                    "mode": "else_check"
                })
        # 解析できない文章の除外
        elif not re.search(self._nouns_pattern, sentence) or re.search("募", sentence):
            pass
        # 投票？
        elif re.search("●|○|▼|▽", sentence):
            """とりあえず保留"""
        # 確認等に使えるか2
        elif re.search("了解|ok|ｏｋ|→", lower_sentence):
            """結果の確認に使えるがとりあえず保留（1より使いにくいので使わない）"""
        # 正規表現で解析するか（COのみ）
        elif (is_negative := "非" in sentence) or re.search("co|ｃｏ", lower_sentence) or "対抗" in sentence:
            format_sentence = re.sub("[^一-龥]", "", sentence)  # 漢字以外を削除
            for role_names in self.roles_list:
                # 一文字ずつ役職名と一致するか確認
                for one_char in format_sentence:
                    if one_char in role_names:
                        role_name = role_names[0]
                        # 否定しているか
                        if is_negative:
                            results.append({
                                "use_engine": "RE",
                                "mode": "co",
                                "target_name": talker_dict["player_name"],
                                "role_name": role_name,
                                "is_negative": True,
                                "is_true_sentence": talker_dict["true_role_name"] != role_name
                            })
                        else:
                            results.append({
                                "use_engine": "RE",
                                "mode": "co",
                                "target_name": talker_dict["player_name"],
                                "role_name": role_name,
                                "is_negative": False,
                                "is_true_sentence": talker_dict["true_role_name"] == role_name
                            })
                            break
                else:
                    continue
                break
        # GiNZAで解析（CO、占霊結果）
        else:
            nouns = self.get_nouns(sentence)
            is_negative = self.get_is_negative(sentence)
            # 取得した名詞のどちらかがが名詞リストに一致するか
            if (len(nouns["else"]) > 2
                    or not nouns["else"]
                    or not ((root_target := re.sub("君$", "", list(nouns["else"])[0])) in self._nouns_list
                    or nouns["root"] in self._nouns_list)):
                return results
            target_name = self.get_full_player_name(root_target)
            # ROOTに役職名が含まれない場合
            if nouns["root"] not in self._role_names_list:
                # RPの可能性あり
                if target_name and talker_dict["co_role_name"] in ["占い師", "霊能者"]:
                    # 占霊結果が出たことにする（ROOTが白や黒以外の場合に状態更新は行わない）
                    results.append({
                        "use_engine": "GiNZA",
                        "mode": "seer" if talker_dict["co_role_name"] == "占い師" else "medium",
                        "target_name": target_name,
                        "team_name": self.get_team_name(nouns['root']),
                        "role_name": nouns['root'],
                        "is_negative": is_negative,
                        "is_true_sentence": talker_dict["true_role_name"] == talker_dict["co_role_name"]
                    })
                return results
            target_role_name = self.get_full_role_name(nouns["root"])
            # 一人称が含まれるか
            if root_target in self.first_persons_list:
                # 否定しているか
                if is_negative:
                    is_true_sentence = talker_dict["true_role_name"] != target_role_name
                else:
                    is_true_sentence = talker_dict["true_role_name"] == target_role_name
                results.append({
                    "use_engine": "GiNZA",
                    "mode": "co",
                    "target_name": talker_dict["player_name"],
                    "role_name": target_role_name,
                    "is_negative": is_negative,
                    "is_true_sentence": is_true_sentence
                })
            elif talker_dict["co_role_name"] in ["占い師", "霊能者"] and target_name:
                results.append({
                    "use_engine": "GiNZA",
                    "mode": "seer" if talker_dict["co_role_name"] == "占い師" else "medium",
                    "target_name": target_name,
                    "team_name": self.get_team_name(target_role_name),
                    "role_name": target_role_name,
                    "is_negative": is_negative,
                    "is_true_sentence": talker_dict["true_role_name"] == talker_dict["co_role_name"]
                })
        return results
