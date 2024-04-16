import jsonlines

def read_jsonl(file_path):
    """
    Read data from a JSONL file
    """
    with jsonlines.open(file_path) as reader:
        return [obj for obj in reader]
