from io import StringIO
import json
import os
from pathlib import Path

import jsonlines

from lib.common import _validate_response
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


def validate_results(file_path):
    """
    Validate the schema of the results file.
    """
    anomalies = []
    with jsonlines.open(file_path, mode='r') as reader:
        for i, record in enumerate(reader):
            try:
                _validate_response(record)
            except ValueError as e:
                anomalies.append((i, str(e)))

    return anomalies


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
            # Download the results
            results = download_results(client, output_file_id)
            formatted_results = format_results(results)
            results_path = asset_base_path / 'result.jsonl'

            with open(results_path, 'w') as f:
                f.write(formatted_results)

            print("Results have been saved.")

            # Validate the results
            # Does not raise an exception, just prints out the anomalies
            anomalies = validate_results(results_path)
            if anomalies:
                print("Anomalies found in the results:")
                for index, error in anomalies:
                    print(f"Record {index}: {error}")
            else:
                print("All results are valid.")

        else:
            print("No output file available.")
    else:
        print("Batch is not yet completed. Please check back later.")


if __name__ == "__main__":
    main()
