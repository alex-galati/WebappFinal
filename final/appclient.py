import requests
import os

port = os.environ['FLASK_PORT']
if not port:
    port = 5000

r = requests.get(f'http://localhost:{port}/')
'''
r = requests.post(
    f'http://localhost:{port}/',
    data={}
)
r = requests.json(
    f'http://localhost:{port}/',
    json={}
)
'''
print(r.text)
