import requests
import json

url = 'http://localhost:11434/api/generate'

payload = {
    "model" : "llama3.2",
    "prompt" : "Why is ollama for free (short answer)"
}

response = requests.post(
    url, json=payload, stream=True
)

if response.status_code == 200:

    # Iterate over streaming response
    for line in response.iter_lines():
        if line:
            # Decode line and parse JSON
            decoded_line = line.decode("utf-8")
            result = json.loads(decoded_line)

            #  Get text from the response
            generated_text = result.get("response", "")
            print(generated_text, end="", flush=True)

    print("Success: ", response.json())
else:
    print("Error: ", response.raise_for_status(), response.text)

