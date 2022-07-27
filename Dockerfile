FROM python:3.8-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip install psycopg2-binary
COPY . /code/
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]