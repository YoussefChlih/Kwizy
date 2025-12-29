import requests
import json

email = 'youssef.chlih.23@ump.ac.ma'
data = {
    'email': email,
    'password': 'TestPass123!',
    'first_name': 'Youssef',
    'last_name': 'Chlih'
}

print(f'Testing signup with: {email}')
resp = requests.post('http://localhost:5000/api/auth/signup', json=data)
print('Status:', resp.status_code)
print('Response:', json.dumps(resp.json(), indent=2))
