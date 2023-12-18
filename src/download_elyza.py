import json
from pathlib import Path

from datasets import load_dataset

# Load the dataset
ds = load_dataset("elyza/ELYZA-tasks-100")

# Function to convert dataset to JSONL format and print
def dataset_to_jsonl(dataset, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for entry in dataset:
            # Construct JSON object
            json_obj = {
                "input_text": entry['input'],
                "output_text": entry['output'],
                "eval_aspect": entry['eval_aspect']
            }

            # Write JSON object to file in JSONL format
            json_str = json.dumps(json_obj, ensure_ascii=False)
            file.write(json_str + '\n')

# Convert and write the dataset to a file in JSONL format
path_jsonl = Path("assets/elyza_tasks_100/dataset.jsonl")

if (path_jsonl.parent is not None) and (not path_jsonl.parent.exists()):
    path_jsonl.parent.mkdir(parents=True, exist_ok=True)

dataset_to_jsonl(ds["test"], path_jsonl)
