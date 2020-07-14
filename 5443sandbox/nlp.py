# coding:utf-8

import spacy
from pprint import pprint

def getLemma(doc):
    lemma_text = ""
    for sent in doc.sents:
        print(sent.root, [child for child in sent.root.children])
        for token in sent:
            lemma_text += token.lemma_
            print(token.i, token.orth_, token.lemma_, token.pos_, token.tag_, token.dep_, token.head.i)
            # if token.dep_ in ["iobj", "nmod"]:
                # print(token.dep_, token.orth_)
    return lemma_text

def getRoots(doc):
    roots = set()
    for sent in doc.sents:
        roots.add(sent.root)
    return roots

if __name__ == "__main__":
    nlp = spacy.load("ja_ginza")

    # 解析する文章
    text = "解析する文章"
    doc = nlp(text)
    json_doc = doc.to_json()

    character = None
    for ent in json_doc["ents"]:
        if ent["label"] == "Person":
            character = doc[ent["start"]]

    # getLemma(doc)

    print(f"{character} = {getRoots(doc)}")

    # spacy.displacy.serve(doc, style="dep", options={"compact":True})
