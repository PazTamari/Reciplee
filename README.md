# Reciplee

## Docker Setup:
You can use docker to run Reciplee backend. To do this, start by cloning Reciplee repository to your server and run the following commands:
```
CD <REPO_FOLDER>/Reciplee
docker build -t reciplee:latest .
docker run -d -v $(pwd):/app -p 80:5000 reciplee:latest
```

## Reciplee App:
Reciplee is a backend application for Google Assistant to help people in the kitchen, built in Python 3.7 and uses Flask with Flask Assistent to support Google Assistant requests and responds.
