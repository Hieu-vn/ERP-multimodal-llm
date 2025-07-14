import requests
import json

url = "http://localhost:8000/query"
headers = {"Content-Type": "application/json"}
data = {"role": "warehouse_manager", "question": "Làm thế nào để kiểm tra tồn kho hiện tại?"}

try:
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
    result = response.json()
    print("--- Functional Test Result ---")
    print(f"Status Code: {response.status_code}")
    print(f"Answer: {result.get('answer', 'No answer field found')}")
    print("Source Documents:")
    for doc in result.get('source_documents', []):
        print(f"  - {doc}")
    print("----------------------------")
except requests.exceptions.RequestException as e:
    print(f"Error during functional test: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response content: {e.response.text}")
except json.JSONDecodeError:
    print(f"Error decoding JSON response: {response.text}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
