import requests

def test_is_alive():
    response = requests.get("http://localhost:5000/swagger")
    assert response.status_code == 200