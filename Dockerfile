FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt pyproject.toml README.md ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
RUN pip install --no-cache-dir --no-deps -e .
EXPOSE 8000
CMD ["uvicorn", "dubbing_pipeline.api:app", "--host", "0.0.0.0", "--port", "8000"]

