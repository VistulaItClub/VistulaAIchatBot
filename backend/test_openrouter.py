import requests
import os

api_key = os.getenv("OPENROUTER_API_KEY")
url = "https://openrouter.ai/api/v1/chat/completions"

data = {
    "model": "openai/gpt-4.1",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 200
}

headers = {"Authorization": f"Bearer {api_key}"}

response = requests.post(url, json=data, headers=headers)
print(response.json())
