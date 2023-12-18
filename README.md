# GPT-4 自動評価スクリプト

GPT-4 を用いて、言語モデルの応答を自動評価するスクリプトである。

## 使用方法

### ELYZA データセットのダウンロード

HuggingFace🤗 から ELYZA-tasks-100 データセットをダウンロードする。

```console
$ docker-compose build
$ docker-compose run gpt4eval python /opt/gpt4eval/download_elyza.py
```

ファイルは `assets/elyza_tasks_100/dataset.jsonl` に保存される。

### 評価

下記のように、`assets/<DATASET_NAME>` にデータセット・LLMの応答を JSONL 形式で配置する。
（フォーマットの詳細は `assets/test` を参照）

`dataset.jsonl` は `assets/elyza_tasks_100` からハードリンク（またはコピー）する。

```
assets/<DATASET_NAME>/
 - dataset.jsonl
 - preds.jsonl
```

その後、下記コマンドを実行する。

```console
$ DATASET_NAME=<DATASET_NAME> docker compose up --build
```

評価結果は JSONL 形式で `assets/<DATASET_NAME>/result.jsonl` に保存される。

## 動作環境

* Linux (kernel 5.15.133.1)
* Docker Compose v2.21.0

## クレジット

* ELYZA-tasks-100: ELYZA (CC BY-SA 4.0), [link](https://huggingface.co/datasets/elyza/ELYZA-tasks-100)

以上
