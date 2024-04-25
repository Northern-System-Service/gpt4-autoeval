import json

import cohere
import requests
import time
from tenacity import retry, stop_after_attempt, wait_random_exponential

from lib.common import validate_response
from lib.client_cohere import client, template_prompt


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(10))
def evaluate(pred, input_text, output_text, eval_aspect):
    """Cohere API により評価を行う
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

    response_raw = client.chat(
        message=prompt,
        model="command-r-plus",
        temperature=0.3,
        tools=[
            {
                "name": "submit_eval",
                "description": "回答の採点結果を登録する",
                "parameter_definitions": {
                    "reason": {
                        "description": "採点基準に照らした評価内容",
                        "type": "str",
                        "required": True,
                    },
                    "grade": {
                        "description": "採点結果、1～5の5段階評価",
                        "type": "int",
                        "required": True,
                    },
                },
            },
        ]
    )
    response = response_raw.tool_calls[0].parameters

    validate_response(response)

    return response
