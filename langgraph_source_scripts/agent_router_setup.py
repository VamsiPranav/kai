from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import JsonOutputParser

def setup_agent_router(local_llm):
    llm = ChatOllama(model=local_llm, format="json", temperature=0)

    prompt = PromptTemplate(
        template="""You are an expert at routing a user question to one of these agents: "inventory-management-agent", "timeline-management-agent", "general-query-agent", "overview-agent", "web-search", or "con_assistant".\n
        Whenever the question is on which products to buy more and which to avoid, or which products to prefer and which to stay away from, or which products are doing well and which are not doing well, then route to "inventory-management-agent". \n
        Whenever the question is on optimal reorder dates and quantities, and potential stock outs, then route to "timeline-management-agent". \n
        Whenever the question is about a particular product, or a particular category, or a any general question, then route to "general-query-agent". \n
        Whenever the question has covers more than one areas (like reorder dates and also which products to buy or stock out alerts and also discounts) or ask more than one question or asks to give "overview", then route them to "overview-agent". \n
        Only when the question is about new products or expanding business or increasing revenue or topics like that, use "web-search". \n
        You do not need to be stringent with the keywords in the question related to these topics. \n
        Route to "con_assistant" if the user inputs any greeting like 'Hi', 'Hello' or any other greeting. Do not be stringent about these particular words, understand if the user is greeting you with any other word. \n

        Give a choice between 'inventory-management-agent' or 'timeline-management-agent' or 'general-query-agent' or 'overview-agent' or 'web-search' or 'con_assistant' based on the question. \n
        Return the a JSON with a single key 'datasource' and no premable or explanation. \n
        Question to route: {question}""",
        input_variables=["question"],
    )

    agent_router = prompt | llm | JsonOutputParser()
    return agent_router

