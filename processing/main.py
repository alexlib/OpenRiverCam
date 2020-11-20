import requests

r = requests.get('http://portal/api/sites')
print(r.text)