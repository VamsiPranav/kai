from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

def setup_question_rewriter(local_llm):
    llm = ChatOllama(model=local_llm, temperature=0)

    re_write_prompt = PromptTemplate(
        template="""
         
         Don't do anything, just return the initial question that you received.
         Here is the initial question: \n\n {question}. Same question with no preamble: \n """,
        input_variables=["question"],
    )

    question_rewriter = re_write_prompt | llm | StrOutputParser()
    return question_rewriter
