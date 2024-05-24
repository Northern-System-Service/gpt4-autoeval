import os
from pathlib import Path
import uuid

import jsonlines

from lib.client_openai import client, template_prompt
from lib.common import get_openai_request_body, read_jsonl

asset_base_path = Path("assets") / os.environ.get("DATASET_NAME")


def prepare_job_requests(model):
    """
    Prepare the job instructions for the batch job
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
            "body": get_openai_request_body(formatted_prompt, model)
        }
        formatted_data.append(batch_request)

    return formatted_data


def prepare_jsonl_data(dataset):
    """
    Prepare the dataset in JSONL format for uploading to OpenAI API
    """
    with jsonlines.open(asset_base_path / "batch_job_requests.jsonl", mode='w') as writer:
        for data in dataset:
            # Assuming `data` is a dictionary with necessary structure
            writer.write(data)


def upload_file(client):
    """
    Upload the JSONL file to OpenAI API
    """
    response = client.files.create(
        file=open(asset_base_path / "batch_job_requests.jsonl", 'rb'),
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


def main(model):
    job_requests = prepare_job_requests(model)
    prepare_jsonl_data(job_requests)

    file_id = upload_file(client)
    print(f"File uploaded, ID: {file_id}")

    batch_id = create_batch(client, file_id)
    print(f"Batch created, ID: {batch_id}")

    # Store or log the batch ID for future retrieval
    with open(asset_base_path / 'batch_id.txt', 'w') as f:
        f.write(batch_id)


if __name__ == "__main__":
    main()
