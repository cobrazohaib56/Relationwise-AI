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
        "content": f"""You are an AI assistant that provides answers from the PDFs and your General Knowledge Base when noting from the publications is found.
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
    "max_tokens": 2000,
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
        
        print(res)
        if res["choices"][0]["message"]["context"]["citations"]:

            payload = {
                "messages": [{
                    "role": "system",
                    "content": f"""You need to check whether both Number 1 and Number 2 are related somehow. If they are not related,
                    you strictly needs to give the answer "No", if they are you will give an answer of "Yes" """
                    },
                    {
                    "role": "user",
                    "content": f"""Number 1: {res["choices"][0]["message"]["context"]["citations"]}
                                Number 2: {user_input}
                                """ 
                    }],
                "temperature": 0.7,
                "top_p": 0.95,
                "max_tokens": 2000
            }
            response_2 = requests.post(url, headers=headers, data=json.dumps(payload))
            if response_2.status_code == 200:
                res_2 = response_2.json()
                answer_2 = res_2["choices"][0]["message"]["content"]
                print()
                print(answer_2)
                print()
                if answer_2 == "Yes":
                    answer = res["choices"][0]["message"]["content"]
                    return answer
                else:
                    payload = {
                "messages": [{
                    "role": "system",
                    "content": f"""You are an AI assistant that provides answers from the PDFs and your General Knowledge Base when noting from the publications is found.
                    You have to keep in mind the history or the context of the converstaion which is {convo_history}"""
                    },
                    {
                    "role": "user",
                    "content": user_input
                    }],
                "temperature": 0.7,
                "top_p": 0.95,
                "max_tokens": 2000
                }
                response_3 = requests.post(url, headers=headers, data=json.dumps(payload))
                if response_3.status_code == 200:
                    res_3 = response_3.json()
                    answer_3 = res_3["choices"][0]["message"]["content"]
                    print()
                    print("Success_3:", answer_3)
                    print()
                    return answer_3
                else:
                    print("Error:", response_1.status_code, response_1.json())


            else:
                print("Error:", response_2.status_code, response_2.json())

        else:
            payload = {
                "messages": [{
                    "role": "system",
                    "content": f"""You are an AI assistant that provides answers from the PDFs and your General Knowledge Base when noting from the publications is found.
                    You have to keep in mind the history or the context of the converstaion which is {convo_history}"""
                    },
                    {
                    "role": "user",
                    "content": user_input
                    }],
                "temperature": 0.7,
                "top_p": 0.95,
                "max_tokens": 2000
            }
            response_1 = requests.post(url, headers=headers, data=json.dumps(payload))
            if response_1.status_code == 200:
                res_1 = response_1.json()
                answer_1 = res_1["choices"][0]["message"]["content"]
                print("Success_1:", answer_1)
                return answer_1
            else:
                print("Error:", response_1.status_code, response_1.json())
    else:
        print("Error:", response.status_code, response.json())
