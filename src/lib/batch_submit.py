import os
from pathlib import Path
import uuid

import jsonlines

from lib.openai_judge import template_prompt
from lib.common import read_jsonl
from lib.openai_client import client

asset_base_path = Path("assets") / os.environ.get("DATASET_NAME")


def load_dataset():
    """
    Load the dataset for processing
    """
    preds = read_jsonl(asset_base_path / "preds.jsonl")
    dataset = read_jsonl(asset_base_path / "dataset.jsonl")

    formatted_data = []

    for pred_data, eval_data in zip(preds, dataset):
        input_text = eval_data["input_text"]
        output_text = eval_data["output_text"]
        eval_aspect = eval_data["eval_aspect"]
        pred = pred_data["pred"]

        # Apply formatting using the existing `template_prompt`
        formatted_prompt = template_prompt.format(
            input_text=input_text,
            output_text=output_text,
            eval_aspect=eval_aspect,
            pred=pred
        )

        # Construct the batch request object per the API documentation
        batch_request = {
            "custom_id": str(uuid.uuid4()),  # Generating a unique ID for each request
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4-1106-preview",
                "response_format": { "type": "json_object" },
                "messages": [
                    {"role": "user", "content": formatted_prompt}
                ],
                "temperature": 0,
                "frequency_penalty": 0,
                "presence_penalty": 0,
            }
        }
        formatted_data.append(batch_request)

    return formatted_data


def prepare_jsonl_data(dataset):
    """
    Prepare the dataset in JSONL format for uploading to OpenAI API
    """
    with jsonlines.open(asset_base_path / "prompt_file.jsonl", mode='w') as writer:
        for data in dataset:
            # Assuming `data` is a dictionary with necessary structure
            writer.write(data)


def upload_file(client):
    """
    Upload the JSONL file to OpenAI API
    """
    response = client.files.create(
        file=open(asset_base_path / "prompt_file.jsonl", 'rb'),
        purpose='batch'
    )
    return response.id


def create_batch(client, input_file_id):
    """
    Create a batch job using the uploaded file
    """
    response = client.batches.create(
        input_file_id=input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h"
    )
    return response.id


def main():
    # Assuming `load_dataset()` is a function that loads your data for processing
    dataset = load_dataset()
    prepare_jsonl_data(dataset)

    file_id = upload_file(client)
    print(f"File uploaded, ID: {file_id}")

    batch_id = create_batch(client, file_id)
    print(f"Batch created, ID: {batch_id}")

    # Store or log the batch ID for future retrieval
    with open(asset_base_path / 'batch_id.txt', 'w') as f:
        f.write(batch_id)


if __name__ == "__main__":
    main()