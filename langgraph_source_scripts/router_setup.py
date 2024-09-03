from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import JsonOutputParser

def setup_router(local_llm):
    llm = ChatOllama(model=local_llm, format="json", temperature=0)

    prompt = PromptTemplate(
        template="""You are an expert at routing a user question to a vectorstore, a web search or a conversation assistant.\n
        Use the vectorstore for questions on overview, stock management, discounts, product specifications or any other store related questions. \n
        You do not need to be stringent with the keywords in the question related to these topics. \n
        Use the Conversation Assistant if the user inputs any greeting like 'Hi', 'Hello' or any other greeting. Do not be stringent about these particular words, understand if the user is greeting you with any other word \n
        Only when the question is about new products or expanding business or increasing revenue or topics like that, use web-search. \n
        Give a choice between 'vectorstore' or 'web_search' or 'con_assistant' based on the question. \n
        Return the a JSON with a single key 'datasource' and no premable or explanation. \n
        Question to route: {question}""",
        input_variables=["question"],
    )

    question_router = prompt | llm | JsonOutputParser()
    return question_router

