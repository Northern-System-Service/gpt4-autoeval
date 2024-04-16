from openai import OpenAI

with open("./assets/prompt_eval.txt") as f:
    template_prompt = f.read()

with open("/run/secrets/OPENAI_API_KEY") as f:
    OPENAI_API_KEY = f.read()

client = OpenAI(api_key=OPENAI_API_KEY)