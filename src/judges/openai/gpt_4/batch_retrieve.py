from io import StringIO
import json
import os
from pathlib import Path

import jsonlines

from lib.common import validate_response
from lib.client_openai import client

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


def reorder_results(results, request_file_path):
    """
    Reorder the results based on the original request order using custom_id.
    """
    # Load the original request order
    request_order = {}
    with jsonlines.open(request_file_path) as reader:
        for index, record in enumerate(reader):
            request_order[record['custom_id']] = index

    # Parse the results into a dictionary keyed by custom_id
    results_dict = {}
    input_stream = StringIO(results)
    reader = jsonlines.Reader(input_stream)
    for record in reader:
        custom_id = record['custom_id']
        results_dict[custom_id] = record

    # Create a new list of results ordered according to the original requests
    ordered_results = [None] * len(request_order)
    for custom_id, index in request_order.items():
        ordered_results[index] = results_dict[custom_id]

    # Convert the ordered results back into a JSONL string
    output_stream = StringIO()
    writer = jsonlines.Writer(output_stream)
    for result in ordered_results:
        if result is not None:
            writer.write(result)
    writer.close()

    return output_stream.getvalue()


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
                validate_response(record)
            except ValueError as e:
                anomalies.append((i, str(e)))

    return anomalies


def main():
    request_file_path = asset_base_path / 'batch_job_requests.jsonl'
    results_file_path = asset_base_path / 'result.jsonl'

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
            results = reorder_results(results, request_file_path)
            formatted_results = format_results(results)

            with open(results_file_path, 'w') as f:
                f.write(formatted_results)

            print("Results have been saved.")

            # Validate the results
            # Does not raise an exception, just prints out the anomalies
            anomalies = validate_results(results_file_path)
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
