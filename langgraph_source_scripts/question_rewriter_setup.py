from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

def setup_question_rewriter(local_llm):
    llm = ChatOllama(model=local_llm, temperature=0)

    re_write_prompt = PromptTemplate(
        template="""
         Re-write the question in a better manner. \n
         Just improve the question to be more descriptive and articulate, do not add any additional details from your side. \n
         Here is the initial question: \n\n {question}. Improved question with no preamble: \n """,
        input_variables=["question"],
    )

    question_rewriter = re_write_prompt | llm | StrOutputParser()
    return question_rewriter
