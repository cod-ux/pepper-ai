# If necessary, install the openai Python library by running 
# pip install openai

from openai import OpenAI
import toml
import requests


secrets = "C:/Users/Administrator/Documents/reporter/secrets.toml"
api_key = toml.load(secrets)["HF"]

API_URL = "https://m0ld0kuoduqn2cnc.us-east-1.aws.endpoints.huggingface.cloud"
headers = {
	"Accept" : "application/json",
	"Authorization": f"Bearer {api_key}",
	"Content-Type": "application/json" 
}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

output = query({
	"inputs": "Who is captain America? Provide a short answer",
	"parameters": {"max_new_tokens": 2048, "return_full_text": False, "temperature": 0.1}
})

print(output[0]["generated_text"])

