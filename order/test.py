import requests

r = requests.post("http://localhost:8000/orders", json={
    "user": "paluch",
    "product": "pizza",
    "price": 42
})
print(r.json())
