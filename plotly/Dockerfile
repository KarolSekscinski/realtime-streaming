FROM python:3.11-alpine

RUN mkdir /webapp

WORKDIR /webapp

ADD requirements.txt ./requirements.txt

RUN apk --no-cache add musl-dev linux-headers gcc && pip install -r ./requiremnets.txt

COPY . /webapp

EXPOSE 8050

CMD [ "python", "./app.py" ]