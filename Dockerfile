FROM python:3.10.13-slim

# Create a non-root user to adress ownership issues
RUN useradd -m myuser

# Install requirements

COPY requirements.txt /tmp/

RUN pip install -r /tmp/requirements.txt

# Copy files to the app dir

COPY src /opt/gpt4eval/

WORKDIR /opt/gpt4eval/

USER myuser

CMD ["python", "/opt/gpt4eval/main.py"]
