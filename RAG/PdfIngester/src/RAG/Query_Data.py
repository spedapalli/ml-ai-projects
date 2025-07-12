# https://github.com/pixegami/langchain-rag-tutorial/blob/main/query_data.py

import argparse
# from Datastore import query_datastore
import Datastore

from langchain.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI


PROMPT_TEMPLATE = """
Answer the question based on the following context :
Service {context}
---
Answer the question based on the above context: {question}
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="Your question for the system")
    args = parser.parse_args()
    query_text = args.query_text
    print(f"Querying for ...... {query_text}")


    #access DB :
    results = Datastore.query_datastore(query_text)
    if (len(results) == 0 or results[0][1] < 0.7):
        print(f"Unable to find matching results")
        return

    # Use ChatGPT to narrow down the Db results
    # - create text to feed to ChatGPT
    context_text = "\n----------\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print(f"PROMPT``````````````````\n{prompt}\n````````````````")

    # Call ChatGPT
    model = ChatOpenAI()
    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("source", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)

if __name__ == "__main__":
    main()
