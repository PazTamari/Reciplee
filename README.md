# Reciplee

## Intro:

## Docker Setup:
You can use docker to run Reciplee backend. To do this, start by cloning Reciplee repository to your server and run the following commands:
```
CD <REPO_FOLDER>/Reciplee
docker build -t reciplee:latest .
docker run -d -v /home/pazta/reciplee/Reciplee/:/app -p 80:5000 reciplee:latest
```

## Reciplee App:
Reciplee is a backend application based on flask_assitant to support Dialogflow fulfillment requests.