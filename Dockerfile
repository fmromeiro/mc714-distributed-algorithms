FROM python:3.10-slim-bullseye
ADD ./foobar /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD ["python", "app.py"]