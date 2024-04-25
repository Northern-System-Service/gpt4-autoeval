# GPT-4（など）自動評価スクリプト

GPT-4 などの LLM を用いて、言語モデルの応答を自動評価するスクリプトである。

## 対応する言語モデル

* `openai/gpt-4`: OpenAI GPT-4 API
* `cohere/command-r-plus`: Cohere Command-R+ API

## 使用方法

### LLM によるテキスト生成

`notebooks` ディレクトリ配下にあるノートブックを実行することで、評価対象のLLMに ELYZA-tasks-100 データセットの各質問に対する回答が生成できる。
ノートブックは、[Google Colaboratory](https://colab.research.google.com/) などで実行可能。

生成されたテキストは `preds.jsonl` という名前の JSONL ファイルに書き出される。
このファイルをダウンロードする。

### ELYZA データセットのダウンロード

HuggingFace🤗 から ELYZA-tasks-100 データセットをダウンロードする。

```console
$ docker compose build
$ docker compose run gpt4eval python /opt/gpt4eval/download_elyza.py
```

ファイルは `assets/elyza_tasks_100/dataset.jsonl` に保存される。

### 評価の準備

下記のように、`assets/<DATASET_NAME>` にデータセット・LLMの応答を JSONL 形式で配置する。
（フォーマットの詳細は `assets/test` を参照）

`dataset.jsonl` は `assets/elyza_tasks_100` からハードリンク（またはコピー）する。

```
assets/<DATASET_NAME>/
 - dataset.jsonl
 - preds.jsonl
```

### 評価: GPT-4 を使う場合

OpenAI API キーを発行し ([link](https://platform.openai.com/api-keys))、 `secrets/OPENAI_API_KEY` に置く (行末は**改行しない**)。

```console
$ cat secrets/OPENAI_API_KEY
my-OPeNAiKeY...
```

評価方法は、下記の2通りから選択できる。

* **`sequential` モード**（デフォルト）: LLMの応答を1つずつ OpenAI API に送信し、評価する。評価結果は、標準出力に順次表示される。
* **`batch` モード**: OpenAI API の[バッチ推論機能](https://platform.openai.com/docs/api-reference/batch) を使用する。結果は 24 時間以内に返却される。API利用料が割安。

#### `sequential` モード

```console
$ DATASET_NAME=<DATASET_NAME> JUDGE=openai/gpt-4 docker compose up --build
```

評価結果は JSONL 形式で `assets/<DATASET_NAME>/result.jsonl` に保存される。

#### `batch` モード

バッチ推論ジョブを作成する。

```console
$ DATASET_NAME=<DATASET_NAME> PROCESS_MODE=batch BATCH_TASK=submit \
        docker compose up --build
```

ジョブIDが `assets/<DATASET_NAME>/batch_id.txt` に保存される。

ジョブの結果を取得する。

```console
$ DATASET_NAME=<DATASET_NAME> PROCESS_MODE=batch BATCH_TASK=retrieve \
        docker compose up --build
```

ジョブが未完了の場合は、その旨が表示される。

ジョブが完了した場合、評価結果は JSONL 形式で `assets/<DATASET_NAME>/result.jsonl` に保存される。

### 評価: Cohere API を使う場合

Cohere API キーを発行し ([link](https://dashboard.cohere.com/api-keys))、 `secrets/COHERE_API_KEY` に置く (行末は**改行しない**)。

```console
$ cat secrets/COHERE_API_KEY
myCohereKey...
```

その後、下記コマンドを実行する。

```console
$ DATASET_NAME=<DATASET_NAME> JUDGE=cohere/command-r-plus docker compose up --build
```

評価結果は JSONL 形式で `assets/<DATASET_NAME>/result.jsonl` に保存される。

### 結果の一覧表示

Google スプレッドシートで結果を一覧表示する場合（[表示例](https://docs.google.com/spreadsheets/d/1nOWtneRdrkxwQbAN0rWmXqiJXR9IXK9lVkyDjQTqNGc/edit?usp=sharing)）は、 `<DATASET_NAME>/{preds,results}.jsonl` を Google Drive にコピーし、`tools/copy_jsonl_to_google_spreadsheet.js` を Google Apps Script として実行する。

## 動作環境

* Linux (kernel 5.15.133.1)
* Docker Compose v2.21.0

## クレジット

* ELYZA-tasks-100: ELYZA (CC BY-SA 4.0), [link](https://huggingface.co/datasets/elyza/ELYZA-tasks-100)

以上
