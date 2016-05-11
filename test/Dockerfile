FROM python:2
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN /usr/local/bin/pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app
CMD ["python", "test.py"]
