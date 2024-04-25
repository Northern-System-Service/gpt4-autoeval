import cohere

with open("./assets/prompt_eval.txt") as f:
    template_prompt = f.read()

with open("/run/secrets/COHERE_API_KEY") as f:
    COHERE_API_KEY = f.read()

client = cohere.Client(COHERE_API_KEY)