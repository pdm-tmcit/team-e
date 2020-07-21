# coding:utf-8
import re
import spacy
from pprint import pprint


def get_nouns(sentence):
    doc = nlp(sentence)
    nouns = {
        "root": "",
        "else": set()
    }
    for chunk in doc.noun_chunks:
        if chunk.root.dep_ not in ["compound", "appos"]:
            if chunk.root.dep_ == "ROOT":
                nouns["root"] = chunk.text
            else:
                nouns["else"].add(chunk.text)
    return nouns


def get_name(sentence):
    doc = nlp(sentence)
    nouns = {
        "root": "",
        "else": set()
    }
    json_doc = doc.to_json()
    if len(json_doc["ents"]):
        ent = json_doc["ents"][0]
        if ent["label"] == "Person":
            nouns["else"].add(doc[ent["start"]])
        for token in json_doc["tokens"]:
            if token["dep"] == "ROOT":
                nouns["root"] = doc[token["head"]]
    return nouns


def get_is_negative(sentence):
    return re.search("ない|なかった|せん", sentence)


if __name__ == "__main__":
    nlp = spacy.load("ja_ginza")

    # 解析する文章
    sentences = [
        "ヨアヒムアウトロー",
        "レジーナは立派なアウトローだった",
        "レジーナはネットアイドル（アウトロー）",
        "俺が警備員（霊能者）だ",
        "私は正義廚(人狼)です"
    ]

    for sentence in sentences:
        nouns = get_nouns(sentence)
        print("名詞分解\t", nouns["else"], "≠" if get_is_negative(sentence) else "=", nouns["root"])
        nouns = get_name(sentence)
        print("名前分解\t", nouns["else"], "≠" if get_is_negative(sentence) else "=", nouns["root"])
        print()
