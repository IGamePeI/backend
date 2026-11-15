FROM python:3.12.6-slim

WORKDIR /app

RUN pip install uv --break-system-packages

COPY pyproject.toml pyproject.toml
RUN uv sync
COPY . .

EXPOSE 8090

CMD [ "uv", "run", "src/main.py"]