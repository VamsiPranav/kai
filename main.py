local_llm = "llama3.1:8b"

import os

from dotenv import load_dotenv

load_dotenv()

# Access environment variables
serper_api_key = os.getenv("SERPER_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")
langchain_tracing_v2 = os.getenv("LANGCHAIN_TRACING_V2")
langchain_endpoint = os.getenv("LANGCHAIN_ENDPOINT")
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")


from langgraph_source_scripts.retriever_setup import LazyRetriever
retriever = LazyRetriever()

from langgraph_source_scripts.guided_retriever_setup import LazyGuidedRetriever
guided_retriever = LazyGuidedRetriever()

from langgraph_source_scripts.overview_retriever import LazyOverviewRetriever
overview_retriever = LazyOverviewRetriever()

from langgraph_source_scripts.retriever_for_abnormal_stock import LazyAbnormalStockRetriever
abnormal_stock_retriever = LazyAbnormalStockRetriever()

from langgraph_source_scripts.retriever_for_top_bottom_setup import LazyTopBottomRetriever
top_bottom_retriever = LazyTopBottomRetriever()

from langgraph_source_scripts.agent_router_setup import setup_agent_router
agent_router = setup_agent_router(local_llm)

from langgraph_source_scripts.retrieval_grader_setup import setup_retrieval_grader
retrieval_grader = setup_retrieval_grader(local_llm)

# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

from langgraph_source_scripts.con_assistant_setup import setup_con_assistant
con_assistant = setup_con_assistant(local_llm)

from langgraph_source_scripts.rag_chain_setup import setup_rag_chain
overview_agent = setup_rag_chain()

from langgraph_source_scripts.inventory_mgmt_agent_setup import setup_inventory_mgmt_agent
inventory_mgmt_agent = setup_inventory_mgmt_agent()

from langgraph_source_scripts.timeline_mgmt_agent import setup_timeline_mgmt_agent
timeline_mgmt_agent = setup_timeline_mgmt_agent()

from langgraph_source_scripts.general_query_agent import setup_general_q_agent
general_q_agent = setup_general_q_agent()

from langgraph_source_scripts.guided_generator_setup import setup_guided_generator
guided_generator = setup_guided_generator()

from langgraph_source_scripts.websearch_joiner_setup import setup_websearch_joiner
websearch_joiner = setup_websearch_joiner()

from langgraph_source_scripts.hallucination_grader_setup import setup_hallucination_grader
hallucination_grader = setup_hallucination_grader(local_llm)


from langgraph_source_scripts.answer_grader_setup import setup_answer_grader
answer_grader = setup_answer_grader(local_llm)

from langgraph_source_scripts.question_rewriter_setup import setup_question_rewriter
question_rewriter = setup_question_rewriter(local_llm)


### Search

# web_search_tool = TavilySearchResults(
#     max_results=5,
#     search_depth="advanced",
#     include_answer=True,
#     include_raw_content=True,
#     include_images=False,
#     include_domains=["https://www.statista.com/outlook/io/manufacturing/consumer-goods/india",
#                      "https://drive.google.com/file/d/1AeG4QiltnG5TUW3YIV9CiETz_PrsVae5/view?usp=sharing"],
#     # exclude_domains=[...],
#     # name="...",            # overwrite default tool name
#     # description="...",     # overwrite default tool description
#     # args_schema=...,       # overwrite default args_schema: BaseModel
# )
from langchain_community.utilities import GoogleSerperAPIWrapper
web_search_tool = GoogleSerperAPIWrapper()

from typing import List
from typing_extensions import TypedDict


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        documents: list of documents
    """

    question: str
    generation: str
    documents: List[str]



### Nodes

def converse(state):
    """
    Converse with the User

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains generated message
    """
    print("---CONVERSE---")
    question = state["question"]

    # Retrieval
    message = con_assistant.invoke(question)
    return {"generation": message, "question": question}

def guided_retrieve(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---GUIDED RETRIEVE---")
    question = state["question"]

    # Retrieval
    documents = guided_retriever.get_relevant_documents(question)
    pprint(documents)
    return {"documents": documents, "question": question}


def general_retrieve(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---GENERAL RETRIEVE---")
    question = state["question"]

    # Retrieval
    documents = retriever.get_relevant_documents(question)
    pprint(documents)
    return {"documents": documents, "question": question}

def overview_retrieve(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---OVERVIEW RETRIEVE---")
    question = state["question"]

    # Retrieval
    documents = overview_retriever.get_relevant_documents(question)
    pprint(documents)
    return {"documents": documents, "question": question}

def abnormal_stock_retrieve(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---STOCK TO DEMAND RETRIEVE---")
    question = state["question"]

    # Retrieval
    documents = abnormal_stock_retriever.get_relevant_documents(question)
    pprint(documents)
    return {"documents": documents, "question": question}

def top_bottom_retrieve(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---BEST & WORST PRODUCTS RETRIEVE---")
    question = state["question"]

    # Retrieval
    documents = top_bottom_retriever.get_relevant_documents(question)
    pprint(documents)
    return {"documents": documents, "question": question}


def overview_generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---OVERVIEW GENERATE---")
    question = state["question"]
    documents = state["documents"]

    # RAG generation
    generation = overview_agent.invoke({"context": documents, "question": question})
    print(generation)
    return {"documents": documents, "question": question, "generation": generation}


def general_generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERAL GENERATE---")
    question = state["question"]
    documents = state["documents"]

    # RAG generation
    generation = general_q_agent.invoke({"context": documents, "question": question})
    print(generation)
    return {"documents": documents, "question": question, "generation": generation}


def inventory_mgmt_generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---INVENTORY MANAGEMENT GENERATE---")
    question = state["question"]
    documents = state["documents"]

    # RAG generation
    generation = inventory_mgmt_agent.invoke({"context": documents, "question": question})
    print(generation)
    return {"documents": documents, "question": question, "generation": generation}


def timeline_mgmt_generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---TIMELINE MANAGEMENT GENERATE---")
    question = state["question"]
    documents = state["documents"]

    # RAG generation
    generation = timeline_mgmt_agent.invoke({"context": documents, "question": question})
    print(generation)
    return {"documents": documents, "question": question, "generation": generation}


def guided_generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]
    generation_p = state["generation"]

    # RAG generation
    generation = guided_generator.invoke({"context": documents, "question": question, "generation": generation_p})
    return {"documents": documents, "question": question, "generation": generation}

def websearch_join(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]

    # RAG generation
    generation = websearch_joiner.invoke({"context": documents, "question": question})
    print(generation)
    return {"documents": documents, "question": question, "generation": generation}



def grade_documents(state):
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with only filtered relevant documents
    """

    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]

    # Score each doc
    filtered_docs = []
    for d in documents:
        score = retrieval_grader.invoke(
            {"question": question, "document": d.page_content}
        )
        grade = score["score"]
        if grade == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            continue
    return {"documents": filtered_docs, "question": question}


def transform_query(state):
    """
    Transform the query to produce a better question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a re-phrased question
    """

    print("---TRANSFORM QUERY---")
    question = state["question"]
    documents = state["documents"]

    # Re-write question
    better_question = question_rewriter.invoke({"question": question})
    pprint(better_question)
    return {"documents": documents, "question": better_question}


def web_search(state):
    """
    Web search based on the re-phrased question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with appended web results
    """

    print("---WEB SEARCH---")
    question = state["question"]
    generation = state["generation"]

    # Web search
    docs = web_search_tool.run(generation)
    # web_results = "\n".join([d["content"] for d in docs])
    # web_results = Document(page_content=web_results)
    print(docs)
    return {"documents": docs, "question": question, "generation": generation}


### Edges ###
def agent_route_question(state):
    """
    Route question to web search or RAG.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---AGENT ROUTE QUESTION---")
    question = state["question"]
    print(question)
    source = agent_router.invoke({"question": question})
    print(source)
    print(source["datasource"])
    if source["datasource"] == "timeline-management-agent":
        print("---ROUTE QUESTION TO TIMELINE MANAGEMENT AGENT---")
        return "timeline-management-agent"
    elif source["datasource"] == "inventory-management-agent":
        print("---ROUTE QUESTION TO INVENTORY MANAGEMENT AGENT---")
        return "inventory-management-agent"
    elif source["datasource"] == "general-query-agent":
        print("---ROUTE QUESTION TO GENERAL QUERY---")
        return "general-query-agent"
    elif source["datasource"] == "overview-agent":
        print("---ROUTE QUESTION TO OVERVIEW AGENT---")
        return "overview-agent"
    elif source["datasource"] == "web-search":
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return "web-search"
    elif source["datasource"] == "con_assistant":
        print("---ROUTE QUESTION TO CONVERSATION---")
        return "con_assistant"


def decide_to_generate(state):
    """
    Determines whether to generate an answer, or re-generate a question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Binary decision for next node to call
    """

    print("---ASSESS GRADED DOCUMENTS---")
    state["question"]
    filtered_documents = state["documents"]

    if not filtered_documents:
        # All documents have been filtered check_relevance
        # We will re-generate a new query
        print(
            "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---"
        )
        return "transform_query"
    else:
        # We have relevant documents, so generate answer
        print("---DECISION: GENERATE---")
        return "generate"


def grade_generation_v_documents_and_question(state):
    """
    Determines whether the generation is grounded in the document and answers question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Decision for next node to call
    """

    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )
    grade = score["score"]

    # Check hallucination
    if grade == "yes":
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        # Check question-answering
        print("---GRADE GENERATION vs QUESTION---")
        score = answer_grader.invoke({"question": question, "generation": generation})
        grade = score["score"]
        if grade == "yes":
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            pprint(generation)
            return "not useful"
    else:
        pprint("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        pprint(generation)
        return "not supported"


from langgraph.graph import END, StateGraph, START
from langgraph.checkpoint.memory import MemorySaver


def create_langgraph_app():

    workflow = StateGraph(GraphState)

    # Define the nodes
    workflow.add_node("converse", converse) # converse
    workflow.add_node("guided_retrieve", guided_retrieve)
    workflow.add_node("top_bottom_retrieve", top_bottom_retrieve)
    workflow.add_node("abnormal_stock_retrieve", abnormal_stock_retrieve)
    workflow.add_node("general_retrieve", general_retrieve)
    workflow.add_node("overview_retrieve", overview_retrieve)
    workflow.add_node("inventory_mgmt_generate", inventory_mgmt_generate)
    workflow.add_node("timeline_mgmt_generate", timeline_mgmt_generate)
    workflow.add_node("general_generate", general_generate)
    workflow.add_node("overview_generate", overview_generate)

    workflow.add_node("web_search", web_search)  # web search

    workflow.add_node("transform_query", transform_query)  # transform_query
    workflow.add_node("guided_generate", guided_generate)
    workflow.add_node("websearch_join", websearch_join)

    # Build graph
    workflow.add_conditional_edges(
        START,
        agent_route_question,
        {
            "con_assistant": "converse",
            "web-search": "guided_retrieve",
            "inventory-management-agent": "top_bottom_retrieve",
            "timeline-management-agent": "abnormal_stock_retrieve",
            "general-query-agent": "general_retrieve",
            "overview-agent": "overview_retrieve"
        },
    )
    workflow.add_edge("guided_retrieve", "websearch_join")
    workflow.add_edge("websearch_join", "web_search")
    workflow.add_edge("web_search", "guided_generate")

    workflow.add_conditional_edges(
        "transform_query",
        agent_route_question,
        {
            "con_assistant": "converse",
            "web_search": "guided_retrieve",
            "inventory-management-agent": "top_bottom_retrieve",
            "timeline-management-agent": "abnormal_stock_retrieve",
            "general-query-agent": "general_retrieve",
            "overview-agent": "overview_retrieve"
        },
    )

    workflow.add_edge("top_bottom_retrieve", "inventory_mgmt_generate")
    workflow.add_edge("abnormal_stock_retrieve", "timeline_mgmt_generate")
    workflow.add_edge("general_retrieve", "general_generate")
    workflow.add_edge("overview_retrieve", "overview_generate")

    workflow.add_edge("guided_generate", END)
    # workflow.add_conditional_edges(
    #     "grade_documents",
    #     decide_to_generate,
    #     {
    #         "transform_query": "transform_query",
    #         "generate": "generate",
    #     },
    # )
    workflow.add_conditional_edges(
        "inventory_mgmt_generate",
        grade_generation_v_documents_and_question,
        {
            "not supported": "inventory_mgmt_generate",
            "useful": END,
            "not useful": "transform_query",
        },
    )
    workflow.add_conditional_edges(
        "timeline_mgmt_generate",
        grade_generation_v_documents_and_question,
        {
            "not supported": "timeline_mgmt_generate",
            "useful": END,
            "not useful": "transform_query",
        },
    )
    workflow.add_conditional_edges(
        "general_generate",
        grade_generation_v_documents_and_question,
        {
            "not supported": "general_generate",
            "useful": END,
            "not useful": "transform_query",
        },
    )
    workflow.add_conditional_edges(
        "overview_generate",
        grade_generation_v_documents_and_question,
        {
            "not supported": "overview_generate",
            "useful": END,
            "not useful": "transform_query",
        },
    )

    workflow.add_edge("converse", END)

    import sqlite3
    from langgraph.checkpoint.sqlite import SqliteSaver
    conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
    memory = SqliteSaver(conn)
    return workflow.compile(checkpointer=memory)

app = create_langgraph_app()

from pprint import pprint

# # Run
# config = {"configurable": {"thread_id": "2"}}
# inputs = {"question": "Give me an overview of the store"}
# for output in app.stream(inputs, config,):
#     for key, value in output.items():
#         continue
#         # Node
#         #pprint(f"Node '{key}':")
#         # Optional: print full state at each node
#         # pprint.pprint(value["keys"], indent=2, width=80, depth=None)
#     #pprint("\n---\n")
#
# # Final generation
# print(value["generation"])