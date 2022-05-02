FROM python:3.9-slim-buster
COPY . .
RUN pip install -r requirements.txt
CMD ["python", scrapper_class.py]