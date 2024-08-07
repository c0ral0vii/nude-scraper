FROM python:3-12slim

RUN apk add --no-cache gcc musl-dev linux-headers

RUN python3 -m venv venv

ENV PATH="/api/venv/bin:$PATH"

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "main.py"]