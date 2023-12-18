import json
import os

import jsonlines

import openai_judge


# Function to read data from a JSONL file
def read_jsonl(file_path):
    with jsonlines.open(file_path) as reader:
        return [obj for obj in reader]


# Load dataset
dataset_name = os.environ.get('DATASET_NAME', 'test')
print(f"dataset_name: {dataset_name}")
preds = read_jsonl(f"assets/{dataset_name}/preds.jsonl")
dataset = read_jsonl(f"assets/{dataset_name}/dataset.jsonl")


with jsonlines.open(f'assets/{dataset_name}/result.jsonl', mode='w') as writer:
    # Evaluate each sample of the dataset, and write the result to the file
    for eval_data, pred_data in zip(dataset, preds):
        pred = pred_data["pred"]
        input_text = eval_data["input_text"]
        output_text = eval_data["output_text"]
        eval_aspect = eval_data["eval_aspect"]

        result = openai_judge.evaluate(pred, input_text, output_text, eval_aspect)
        writer.write(result)

        print(f"==============================")
        print(f"Q. {input_text}")
        print(f"A. {pred}")
        print(f"GPT-4. {result}")
        print(f"")
