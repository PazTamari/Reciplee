# Dockerfile - this is a comment. Delete me if you want.
FROM python:3.7.4-alpine
# COPY ./ /app
# WORKDIR /app
COPY ./requirements.txt .
RUN pip install -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["/app/app.py"]