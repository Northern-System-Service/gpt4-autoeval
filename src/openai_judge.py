import json

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential


with open("./assets/prompt_eval.txt") as f:
    template_prompt = f.read()

with open("/run/secrets/OPENAI_API_KEY") as f:
    OPENAI_API_KEY = f.read()

client = OpenAI(api_key=OPENAI_API_KEY)


def evaluate(pred, input_text, output_text, eval_aspect):
    """OpenAI API により評価を行う
    Args:
    Returns:
        [dict] 評価結果
        {"reason": "<評価理由>", "grade": <int, 1～5の5段階評価>}
    """
    # `pred` が空の場合は、評点を1にする
    if (pred == ""):
        return {"reason": "No response", "grade": 1}

    prompt = template_prompt.format(
        input_text=input_text,
        output_text=output_text,
        eval_aspect=eval_aspect,
        pred=pred,
    )

    response_raw = completion_with_backoff(
        model="gpt-4-1106-preview",
        #model="gpt-3.5-turbo-1106",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        frequency_penalty=0,
        presence_penalty=0,
    )
    response = json.loads(response_raw.choices[0].message.content)

    _validate_schema(response)

    return response


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


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion_with_backoff(**kwargs):
    return client.chat.completions.create(**kwargs)
