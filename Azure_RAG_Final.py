import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Define your API base URL, deployment ID, and API key
api_key = os.getenv("OPENAI_API_KEY")  # Replace with your actual API key

# Define the endpoint URL
url = "https://relationwiseai4136950365.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"

# Define headers
headers = {
    "Content-Type": "application/json",
    "api-key": api_key
}

def azure_payload(user_input, convo_history):
    # Define the payload
    payload = {
    "messages": [
        {
        "role": "system",
        "content": f"""You are an AI assistant that provides answers without including citations or references to source documents. 
        You have to keep in mind the history or the context of the converstaion which is {convo_history}"""
        },
        {
        "role": "user",
        "content": user_input
        }
    ],
    "temperature": 0.7,
    "top_p": 0.95,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "max_tokens": 800,
    "stop": None,
    "data_sources": [
        {
        "type": "azure_search",
        "parameters": {
            "filter": None,
            "endpoint": "https://relationwise-ai-searchservice2.search.windows.net",
            "index_name": "vector-search-index-1",
            "semantic_configuration": "azureml-default",
            "authentication": {
            "type": "api_key",
            "key": os.getenv("AZURE_AI_SEARCH_KEY")
            },
            "query_type": "simple",
            "in_scope": True,
            "role_information": "You are an AI assistant that helps people find information.",
            "strictness": 3,
            "top_n_documents": 5
        }
        }
    ]
    }


    # Send the POST request
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Check the response
    if response.status_code == 200:
        res = response.json()
        if res["choices"][0]["message"]["context"]["citations"]:
            answer = res["choices"][0]["message"]["content"]
            print("Success:", answer)
            return answer
        else:
            payload = {
                "messages": [{
                    "role": "system",
                    "content": f"""You are an AI assistant that provides answers without including citations or references to source documents. 
                    You have to keep in mind the history or the context of the converstaion which is {convo_history}"""
                    },
                    {
                    "role": "user",
                    "content": user_input
                    }],
                "temperature": 0.7,
                "top_p": 0.95,
                "max_tokens": 800
            }
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                res_1 = response.json()
                answer_1 = res_1["choices"][0]["message"]["content"]
                print("Success_1:", answer_1)
                return answer_1
            else:
                print("Error:", response.status_code, response.json())
    else:
        print("Error:", response.status_code, response.json())
