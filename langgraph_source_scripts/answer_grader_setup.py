from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

def setup_answer_grader(local_llm):
    llm = ChatOllama(model=local_llm, format="json", temperature=0)

    prompt = PromptTemplate(
        template="""You are a Stock Management Expert who is now assessing whether an answer given by a stock management intern is useful to resolve a question.\n
        The stock management intern was asked to provide business intelligence insights on the question and the said intern looked at the data required pertaining the business and gave the following answer. \n
        Here is the answer:
        \n ------- \n
        {generation} 
        \n ------- \n
        Here is the question: {question}
        Be very lenient with your judgement, only score a 'no' when you think that the answer is extremely unrelated to the question. Almost always, score a 'yes'. \n
        Give a binary score 'yes' or 'no' to indicate whether the answer is useful to resolve a question. \n
        Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.""",
        input_variables=["generation", "question"],
    )

    answer_grader = prompt | llm | JsonOutputParser()
    return answer_grader
