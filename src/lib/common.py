import jsonlines

def read_jsonl(file_path):
    """
    Read data from a JSONL file
    """
    with jsonlines.open(file_path) as reader:
        return [obj for obj in reader]


def _validate_schema(response: dict):
    """response を JSON としてパースし、下記のスキーマに合致することを確かめる
    {"reason": "<評価理由>", "grade": <int, 1～5の5段階評価>}

    Raises:
        ValueError
    """
    if not isinstance(response, dict):
        raise ValueError("Response is not a JSON object")

    required_keys = {"reason", "grade"}

    if not required_keys.issubset(response.keys()):
        raise ValueError("Missing required keys")

    if not isinstance(response['reason'], str):
        raise ValueError("'reason' should be a string")

    if not isinstance(response['grade'], int) or not (1 <= response['grade'] <= 5):
        raise ValueError("'grade' should be an integer between 1 and 5")
