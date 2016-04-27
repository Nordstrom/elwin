FROM python:2-alpine
COPY . /usr/src/myapp
WORKDIR /usr/src/myapp
RUN pip install -r requirements.txt
CMD ["python", "test.py"]
