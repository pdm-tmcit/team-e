import csv
import re
import spacy

nlp = spacy.load('ja_ginza')
path = input()

def name(text):
    tag = [t.tag_ for t in nlp(text)]
    for i in tag:
        if re.match(r'名詞-固有名詞', i):
            return False
    return True

with open(path, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    l = [row for row in reader]

i = 0
path_w = 'data.txt'
with open(path_w, mode='w', encoding='utf=8') as fi:

    while l[i][0] == "プロローグ":
        text = l[i][3]
        if name(text):
            text = l[i][3].split('。')
            for txt in text:
                if "■" in txt:
                    i = i + 1
                elif "□" in txt:
                    i = i + 1
                elif ">" in txt:
                    i = i + 1
                elif "(" in txt:
                    i = i + 1
                elif "…" in txt:
                    i = i + 1
                elif "・" in txt:
                    i = i + 1
                elif "【" in txt:
                    i = i + 1
                elif "（" in txt:
                    i = i + 1
                else:
                    fi.write(txt + "\n")
                    i = i + 1
        else:
            i = i + 1
