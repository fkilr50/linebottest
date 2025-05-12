import requests
import json

def test_webhook():
    """
    This function sends a POST request to the Flask webhook API with a sample question
    and prints the response from the server.
    """
    url = "http://127.0.0.1:5000/webhook"
    
    # Simulate a question to the webhook (e.g., "What is renewable energy?")
    test_data = {
        "events": [
            {
                "message": {
                    "text": "What is renewable energy?"
                }
            }
        ]
    }

    # Send POST request to Flask app
    response = requests.post(url, json=test_data)
    
    # Print the response from the server
    print(response.json())

if __name__ == "__main__":
    test_webhook()
