import requests
import json
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()

# Define your API base URL, deployment ID, and API key
api_key = os.getenv("OPENAI_API_KEY")  # Replace with your actual API key
# api_key = st.secrets["OPENAI_API_KEY"]
azure_search_key = os.getenv("AZURE_AI_SEARCH_KEY")
# azure_search_key = st.secrets["AZURE_AI_SEARCH_KEY"]
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
        "content": f"""You are an AI assistant that provides answers from the PDFs and your General Knowledge Base, when nothing from the publications is found.
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
            "key": azure_search_key
            },
            "embedding_dependency": {
              "type": "endpoint",
              "endpoint": "https://relationwiseai4136950365.openai.azure.com/openai/deployments/text-embedding-ada-002/embeddings?api-version=2023-05-15",
              "authentication": {
                "type": "api_key",
                "key": "4dM411oyDK5qWQoTlmcJbwDg5fzatzCcUi6Se87DbU0k32d5luK1JQQJ99AKACfhMk5XJ3w3AAAAACOG7ENB"
              }
            },
            "query_type": "vector_simple_hybrid",
            "in_scope": True,
            "role_information": "You are an AI assistant that helps people find information.",
            "strictness": 3,
            "top_n_documents": 3,
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
                    "content": f"""
                    You need to check the relevence of both "Number 1" and "Number 2. You have to handle 2 things here.
                    
                    NOTE: Do not say anything about their relevence in your response

                    If both "Number 1" and "Number 2" are not related, you need to give a general response for the user query which is the 
                    Number 1, this one : {user_input}. Please Keep in mind you need to give a response of it from your own Knowledge base.
                    
                    If both of "Number 1" and "Number 2" are related you strictly need to say "Yes"  """
                    },
                    {
                    "role": "user",
                    "content": f"""Number 1: {res["choices"][0]["message"]["context"]["citations"]}
                                Number 2: {user_input}
                                """ 
                    }],
                "temperature": 0.7,
                "top_p": 0.95,
                "max_tokens": 800
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
                    return answer_2
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
                "max_tokens": 800
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
