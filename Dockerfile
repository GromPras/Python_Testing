FROM python:3.13-slim

RUN python -m venv venv
ENV PATH="venv/bin:$PATH"

RUN pip install -r requirements.txt

COPY src /src

WORKDIR /src

CMD flask run --host=0.0.0.0 --port=8888
