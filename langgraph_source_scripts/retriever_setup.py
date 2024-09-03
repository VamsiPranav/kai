import os
from typing import List
from xml.dom.minidom import Document

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import Chroma
from langchain_nomic.embeddings import NomicEmbeddings
from langchain.schema import BaseRetriever


class LazyRetriever:
    def __init__(self):
        self._retriever: BaseRetriever | None = None

    def __call__(self) -> BaseRetriever:
        if self._retriever is None:
            self._retriever = self._setup_retriever()
        return self._retriever

    def _setup_retriever(self) -> BaseRetriever:
        csv_files = [
            "data/retrieval_table.csv",
        ]

        # Load CSV files
        docs = []
        for file in csv_files:
            if not os.path.exists(file):
                raise FileNotFoundError(f"CSV file not found: {file}")
            loader = CSVLoader(file_path=file)
            docs.extend(loader.load())

        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=250, chunk_overlap=0
        )
        doc_splits = text_splitter.split_documents(docs)

        try:
            vectorstore = Chroma.from_documents(
                documents=doc_splits,
                collection_name="csv-rag-chroma",
                embedding=NomicEmbeddings(model="nomic-embed-text-v1.5", inference_mode="local"),
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create vector database: {str(e)}")

        # Retrieves all documents
        return vectorstore.as_retriever()

    def get_relevant_documents(self, query: str) -> List[Document]:
        retriever = self()
        all_docs = retriever.get_relevant_documents(query)
        return all_docs
