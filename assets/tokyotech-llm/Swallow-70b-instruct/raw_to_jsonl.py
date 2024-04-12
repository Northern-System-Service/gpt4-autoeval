import re
import json

# First, I will open and read the contents of the provided file to understand its structure.
file_path = './raw.txt'

with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# The function to extract and format the answers into JSONL format
def extract_answers_to_jsonl(text):
    # Split the text into blocks using the pattern "Q. " as the separator
    blocks = re.split(r'\nQ\. ', text)
    jsonl_lines = []

    # Process each block to extract the answer
    for block in blocks:
        # Find the answer part which starts with "A. "
        match = re.search(r'A\. (.+)\n\nLlama.generate: prefix-match hit\n\n==============================', block, re.DOTALL)
        if match:
            # Extract the answer and format it into JSONL
            answer = match.group(1).strip()
            jsonl_line = json.dumps({"pred": answer}, ensure_ascii=False)
            jsonl_lines.append(jsonl_line)

    return jsonl_lines

# Extract and convert the answers to JSONL format
jsonl_content = extract_answers_to_jsonl(content)

# Display the first few lines of the converted content for verification
for l in jsonl_content:
    print(l)
