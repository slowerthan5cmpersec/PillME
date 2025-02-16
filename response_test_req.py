import requests

url = 'http://127.0.0.1:8000/generate/'
data = {'query' : '대한민국의 수도는 어디지? 대한민국의 대통령은 누구지?'}

with requests.post(url, stream=True, json=data) as res:
    for line in res.iter_content(chunk_size=None):
        if line != ' ':
            print(line.decode('utf-8', errors="ignore"), flush=True)


