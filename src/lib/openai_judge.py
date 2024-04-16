import json

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential

from lib.common import _validate_schema
from lib.openai_client import client, template_prompt


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


def completion_with_backoff(**kwargs):
    return client.chat.completions.create(**kwargs)
