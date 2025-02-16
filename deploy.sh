docker build -t slowe_fastapi:0.1 -f Dockerfile .
docker run -p 80:80 slowe_fastapi:0.1