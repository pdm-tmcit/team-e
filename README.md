# team-e

## 開発環境

| 種類                         | 名前                     |
| ---------------------------- | ------------------------ |
| 使用言語                     | Python3.8                |
| コーディング規約             | PEP8                     |
| Code Formatter               | autopep8                 |
| Lint                         | flake8                   |
| 統合開発環境やそのプラグイン | AtomやVisual Studio Code |
| ビルドツール                 | pip                      |
| 単体テストの方針とライブラリ | unittest         |
| 結合テスト用のCI             | unittest           |
| コードカバレッジ             | Codecov                  |
| ブランチ管理の方針           | GitHub Flow              |

[全部入りVM](https://drive.google.com/file/d/1B-y4uK_MsaQQOxx7CY5OWhn8d81WZ4Mu/view?usp=sharing)

## 使い方

```
$ python main.py [ログファイル名.csv]
```
会話を解析し空文字があったら埋める。
その結果を`/results/ログファイル名.csv`に出力する。

## 単体テスト

```
$ python -m unittest [テストファイル名.py]
```
* test_game.py
  プログラム内に読み込むログファイルを記述する。解析結果が全て出力されるため目視で内容を確認する。

* test_template.py
  プログラム内にテストしたいパターンを記述する。一つでも空文字が出力されたらエラーとなる。
  内容は目視で確認する。

* test_chatbot.py
  プログラム内にテストしたい例文を記述する。一つでも空文字が出力されたらエラーとなる。
  内容は目視で確認する。

## 結合・総合テスト

```
$ python -m unittest test_integration.py
```
プログラム内に読み込むログファイルを記述する。
出力ファイルの会話に一つでも空文字があったらエラーとなる。（結合テスト）
結合テストが通った場合、出力ファイルの中身を目視で確認する。（総合テスト）

## chatbotクラス仕様

## HackMD

[要件定義案1](https://hackmd.io/rXndBdSgRNSAV0mRnjowHw)

[要件定義案2](https://hackmd.io/2t6dxpqsRZCb6xwm20pQtg)

[開発方針](https://hackmd.io/zsmRI8reQHmQ9Ca7rXRw1w)
