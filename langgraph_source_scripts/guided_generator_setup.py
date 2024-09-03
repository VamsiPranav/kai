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

def setup_guided_generator():

    prompt = PromptTemplate(
        template="""You are provided with a few products that are doing well at the super market (the store run by the user) based on their Product Viability Score and Shelf Score. \n
        Shelf life score is a measure of how quickly a product sells relative to its shelf life \n
        The Product Viability Score is a comprehensive metric that combines multiple factors to give an overall assessment of a product's performance and profitability. \n
        The Products that are provided in the generation are products currently in the store with high Viability and Shelf Scores. \n
        Hence these products are doing well. \n
        
        You are provided a list of new products in context from a web search similar to the ones does well right now. \n
        Summarize this and convey to the user that, for increasing his product line or grow his business, he could consider adding these products to the store since similar products have done well. \n
        
        Do mention the products in generation and say that they have high viability and shelf scores and hence the new products are found similar to those. \n
        question: {question}
        context: {context}
        generation: {generation}
        """,
        input_variables=["question", "context", "generation"],

    )

    guided_generator = prompt | llm | StrOutputParser()
    return guided_generator
