import json

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential

from lib.common import validate_response, get_openai_request_body
from lib.client_openai import client, template_prompt


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(10))
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
        **get_openai_request_body(prompt)
    )
    response = json.loads(response_raw.choices[0].message.content)

    validate_response(response)

    return response


def completion_with_backoff(**kwargs):
    return client.chat.completions.create(**kwargs)
