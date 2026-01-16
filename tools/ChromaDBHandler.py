from langchain_chroma import Chroma
#from langchain_classic.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.embeddings import SentenceTransformerEmbeddings
# from langchain_huggingface import HuggingFaceEmbeddings

import os
from dotenv import load_dotenv
load_dotenv()

class ChromaDBHandler:
    def __init__(self, logger):
        self.logger=logger
        self.modelName=os.getenv("SENTENCE_TRANSFORMER_MODEL")
        self.embeddings = SentenceTransformerEmbeddings(model_name=self.modelName)
        self.vector_store = Chroma(
            collection_name=os.getenv("COLLECTION_NAME"), #"DH_News_Collection",
            embedding_function=self.embeddings,
            persist_directory=os.getenv("CHROMADB_PATH"),# "./chroma_db_news_db",  # Where to save data locally, remove if not necessary
        )
    
    
    def add_splits_to_db(self, documents):
        news_id = documents[0].metadata["news_id"]
        existing = self.vector_store.get(where={"news_id": news_id})
        
        if not existing["ids"]:
            document_ids = self.vector_store.add_documents(
                documents=documents, 
                ids=[doc.id for doc in documents]
            )
            self.logger.info(f"{ChromaDBHandler.__name__}: Splited documents loaded to ChromaDB with ids: {news_id}")
        else:
            self.logger.info(f"{ChromaDBHandler.__name__}: Splited documents already saved to ChromaDB with ids: {news_id}")
        
        return

    # retriever.
    def retrieve_documents_from_chromadb(self):
        return self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 10,
                "fetch_k": 20
            }
        )



