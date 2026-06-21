import requests
import time

def test_prediction():
    url = "http://127.0.0.1:8000/api/predict"
    payload = {
        "rainfall": 80.5,
        "temperature": 15.2,
        "elevation": 4500,
        "lake_area": 2.5,
        "glacier_area": 10.0,
        "humidity": 85.0
    }
    
    print("Sending test prediction request to backend...")
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Response received:", response.json())
        print("This prediction and any associated alerts should now be in your MongoDB Atlas cluster!")
    except Exception as e:
        print(f"Error during request: {e}")

if __name__ == "__main__":
    test_prediction()
