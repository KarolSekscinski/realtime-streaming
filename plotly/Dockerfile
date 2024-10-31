FROM python:3.11-alpine

RUN mkdir /app

WORKDIR /app

ADD requirements.txt ./requirements.txt

RUN apk --no-cache add musl-dev linux-headers gcc && pip install -r ./requirements.txt

COPY src/ .

EXPOSE 8050

CMD [ "python", "main/app.py" ]