# Reciplee

# Docker process
You can use docker to run Reciplee:
* Clone this git repository
* CD to Reciplee/docker folder
* To build the docker image: docker build -t reciplee:latest .
* To run the container: docker run -d -v /home/pazta/reciplee/Reciplee/:/app -p 80:5000 reciplee:latest