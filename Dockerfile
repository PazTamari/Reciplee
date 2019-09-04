# Dockerfile - this is a comment. Delete me if you want.
FROM python:3.7.4-alpine
# COPY ./ /app
# WORKDIR /app
COPY ./requirements.txt .

RUN apk add build-base \
    && apk add python3-dev \
    && apk add --no-cache libressl-dev musl-dev libffi-dev

RUN pip install -r requirements.txt



ENTRYPOINT ["python3"]
CMD ["/app/app.py"]