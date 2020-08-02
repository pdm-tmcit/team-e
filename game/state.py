# coding:utf-8
import re
from pprint import pprint
from termcolor import colored
from .nlp import NLP
from template.template import TemplateResponder
from chatbot.chatbot import Chatbot


class WareWolfGame:

    def __init__(self, log_data, config={}):
        self.config = {
            "test_mode": False,
            "use_template_row_count": 10
        }
        self.config.update(config)
        self.responder = {
            "template": TemplateResponder(),
            "chatbot": Chatbot()
        }
        self._nlp = NLP()
        self._log_data = log_data
        self.generate_log_data = log_data
        self.players_count = 0
        self.loaded_log_count = 0
        self.last_day = 0
        self.end_flag = False
        self.joined_players_list = []
        self.players_co_dict = {}
        self.nlp_results_list = []
        self.player_checked_list = []

    def show_state(self):
        pprint(self.players_co_dict)
        print()
        pprint(self.nlp_results_list)
        print()
        pprint(self.player_checked_list)

    def load_prologue(self):
        for index, [now_day_text, player_name, true_role_name, *talks_list] in enumerate(self._log_data):
            if now_day_text != "プロローグ":
                break
            talks_text = "".join(talks_list)
            # プロローグ中に抜けた人がいるか
            if (player_name == "楽天家ゲルト"
                    and (target_name := re.findall("急用により(.+?)は旅立ったよ", talks_text))
                    and (player_name := self._nlp.get_full_player_name(target_name, self.joined_players_list))):
                self.players_co_dict.pop(player_name)
            # RPっぽいか
            if re.search("=|＝|rp", talks_text.lower()):
                pass
            if player_name not in self.players_co_dict:
                self.players_co_dict[player_name] = {
                    "true_role_name": true_role_name,
                    "not_role_names": set()
                }
                self.joined_players_list.append([player_name, *self._nlp.all_players_dict[player_name]])
            self.loaded_log_count += 1
        self.players_count = len(self.players_co_dict)
        self._nlp.set_joined_players(self.joined_players_list)
        return self.players_count > 0

    def next_day(self):
        if self.loaded_log_count == 0:
            print("プロローグが読み込まれていません。")
            return False
        if self.end_flag:
            print("会話は終了しました")
            return False
        self.last_day += 1
        self.nlp_results_list.append({
            "co": {},
            "seer": {},
            "medium": {}
        })
        self.player_checked_list.append({
            "co": {},
            "else": {}
        })
        for index, [now_day_text, player_name, true_role_name, *talks_list] in enumerate(self._log_data[self.loaded_log_count:]):
            if self.last_day != int(re.sub("[^0-9]", "", now_day_text)):
                break
            log_index = index + self.loaded_log_count + 1
            talks_text = "".join(talks_list)
            if not talks_text:
                generated_sentence = self.generate_response(log_index, self._log_data[log_index - 2][3])
                self.generate_log_data[log_index - 1][3] = generated_sentence
                print(colored(f"BLANK：\t空欄\t{log_index} {player_name} {true_role_name} {generated_sentence}", "blue"))
                continue
            # 【】で括られた文章の抜き取り
            if not (sentences := re.findall(r"【((?!>>\d|\d{2}:\d{2}).+?)】", talks_text)):
                continue
            for sentence in sentences:
                if self.config["test_mode"]:
                    print(f"\n{log_index} {player_name} {sentence}")
                results = self._nlp.parse({
                    "player_name": player_name,
                    "true_role_name": true_role_name,
                    "co_role_name": self.players_co_dict[player_name].get("co_role_name")
                }, sentence)
                for r in results:
                    comp_text = '≠' if r.get("is_negative") else '='
                    if r["mode"] == "co":
                        self.nlp_results_list[-1]["co"][player_name] = log_index
                        if r["is_negative"]:
                            self.players_co_dict[r["target_name"]]["not_role_names"].add(r["role_name"])
                        else:
                            self.players_co_dict[r["target_name"]]["co_role_name"] = r["role_name"]
                        color = "green" if r["is_true_sentence"] else "red"
                        colored_text = colored(f"{r['use_engine']}：\tCO\t{log_index} {r['target_name']} {comp_text} {r['role_name']}", color)
                        print(colored_text)
                    elif r["mode"] == "co_check":
                        self.player_checked_list[-1]["co"][player_name] = log_index
                        colored_text = colored(f"{r['use_engine']}：\tCO確\t{log_index} {player_name}", "yellow")
                        print(colored_text)
                    elif r["mode"] == "else_check":
                        if self.last_day == 1:
                            continue
                        self.player_checked_list[-1]["else"][player_name] = log_index
                        colored_text = colored(f"{r['use_engine']}：\t占霊確\t{log_index} {player_name}", "yellow")
                        print(colored_text)
                    else:
                        if self.last_day == 1:
                            continue
                        self.nlp_results_list[-1][r["mode"]][player_name] = {
                            "log_index": log_index,
                            "target_name": r["target_name"],
                            "team_name": r["team_name"],
                            "role_name": r["role_name"]
                        }
                        color = "green" if r["is_true_sentence"] else "red"
                        mode = '占い師' if r['mode'] == 'seer' else '霊能者'
                        colored_text = colored(f"{r['use_engine']}：\t{mode}\t{log_index} {r['target_name']} {comp_text} {r['role_name']}", color)
                        print(colored_text)
        else:
            self.end_flag = True
        self.loaded_log_count += index
        return not self.end_flag

    def generate_response(self, now_log_index, sentence):
        today_nlp_result_dict = self.nlp_results_list[-1]
        if (last_log_index := max([0, *today_nlp_result_dict["co"].values()])) and now_log_index <= last_log_index + self.config["use_template_row_count"]:
            return self.responder["template"].response("co")
        if len(today_nlp_result_dict["seer"]) or len(today_nlp_result_dict["medium"]):
            last_seer_log_index = max([0, *[player["log_index"] for player in today_nlp_result_dict["seer"].values()]])
            last_medium_log_index = max([0, *[player["log_index"] for player in today_nlp_result_dict["medium"].values()]])
            mode = "seer" if last_seer_log_index >= last_medium_log_index else "medium"
            last_log_index = max([last_seer_log_index, last_medium_log_index])
            if now_log_index <= last_log_index + self.config["use_template_row_count"]:
                for r in today_nlp_result_dict[mode].values():
                    if r["log_index"] == last_log_index:
                        target_name = self._nlp.all_players_dict[r["target_name"]][0]
                        return self.responder["template"].response(mode, target_name, r['team_name'])
        return self.responder["chatbot"].response(sentence)
