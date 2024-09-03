from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser

import os
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
    temperature=0,
    max_tokens=1024,
    timeout=None,
    max_retries=2,
    # other params...
)

def setup_websearch_joiner():

    prompt = PromptTemplate(
        template="""You are a web-search query writer who needs to output a query to search on the web. \n
        No matter what the input question is, always do the following: \n
        
        You are provided with a list of Products. \n
        Convert each of them into plain English in the format of 'Product Brand' + 'Product Name'. \n
        Let's call the list of these products as 'products_list'. \n
        Write an English query to find products that are similar to that. \n
        No matter what the input question is, always output the query to be 'Find Indian CPG Products Similar to -products_list-'. \n
        Remember to replace -products_list- with actual products. \n
        The final query should be 'Find Indian CPG Products Similar to products_list'. \n
        Do not putput the json of products_list as is. \n
        Only output the final query and nothing else in the form of a single string. \n
        question: {question}
        context: {context}
        """,
        input_variables=["question", "context"],

    )

    websearch_joiner = prompt | llm | StrOutputParser()
    return websearch_joiner
