from io import StringIO
import json
import os
from pathlib import Path

import jsonlines

from lib.openai_client import client

asset_base_path = Path("assets") / os.environ.get("DATASET_NAME")


def retrieve_batch(client, batch_id):
    """
    Retrieves the specified batch job and checks its status.
    """
    batch = client.batches.retrieve(batch_id)
    return batch


def download_results(client, file_id):
    """
    Download the file using the given file ID and return its content.
    """
    return client.files.retrieve_content(file_id)


def format_results(results):
    """
    Process the raw results to extract the 'content' field, and return formatted results.
    """
    input_stream = StringIO(results)
    output_stream = StringIO()
    reader = jsonlines.Reader(input_stream)
    writer = jsonlines.Writer(output_stream)

    for record in reader:
        # Extract the nested content
        content_string = record.get("response", {}).get("body", {}).get("choices", [{}])[0].get("message", {}).get("content", "{}")
        # Parse the content JSON string
        content_data = json.loads(content_string)
        # Write the parsed content data to the output stream
        writer.write(content_data)

    # Make sure to flush the writer to ensure all data is written to the output stream
    writer.close()
    # Return the formatted results as a string
    return output_stream.getvalue()


def main():
    # Load the batch ID from file
    with open(asset_base_path / 'batch_id.txt', 'r') as f:
        batch_id = f.read().strip()

    # Retrieve the batch info
    batch = retrieve_batch(client, batch_id)
    print(f"Batch status: {batch.status}")

    if batch.status == "completed":
        print("Batch completed. Downloading results...")
        output_file_id = batch.output_file_id

        if output_file_id:
            results = download_results(client, output_file_id)
            formatted_results = format_results(results)

            with open(asset_base_path / 'batch_results.jsonl', 'w') as f:
                f.write(formatted_results)

            print("Results have been saved.")
        else:
            print("No output file available.")
    else:
        print("Batch is not yet completed. Please check back later.")


if __name__ == "__main__":
    main()
