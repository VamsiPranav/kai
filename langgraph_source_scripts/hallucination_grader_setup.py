from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

def setup_hallucination_grader(local_llm):
    llm = ChatOllama(model=local_llm, format="json", temperature=0)

    prompt = PromptTemplate(
        template="""You are a grader assessing whether an answer is generated from a given document. \n 
        Here are the facts:
        \n ------- \n
        {documents} 
        \n ------- \n
        Here is the answer: {generation}
        Be very lenient with your judgement, the answer is generated after a series of analysis of the documents and might not exactly reflect the facts in a document. \n
        Even if it matches with the document slightly, it means that the answer is generated from the document. \n
        Only score the answer a 'no' when you think that the answer is purely fictional and has no relation whatsoever with the document. \n
        Score a 'no' when the answer has python code. \n
        Give a binary score 'yes' or 'no' score to indicate whether the answer is generated from the document. \n
        Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.""",
        input_variables=["generation", "documents"],
    )

    hallucination_grader = prompt | llm | JsonOutputParser()
    return hallucination_grader
