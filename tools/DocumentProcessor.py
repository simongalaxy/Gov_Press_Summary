from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_text_splitters import MarkdownTextSplitter

from pprint import pformat
import os
from dotenv import load_dotenv
load_dotenv()

class DocumentProcessor:
    def __init__(self, logger):
        self.logger = logger
        self.modelName = os.getenv("OLLAMA_EMBEDDING_MODEL")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,  # chunk size (characters)
            chunk_overlap=250,  # chunk overlap (characters)
            add_start_index=True,  # track index in original document
        )
    
    def split_text_from_news(self, text):
        all_splits = self.text_splitter.split_text(text=text)
        self.logger.info(f"{DocumentProcessor.__name__}: Split press release into {len(all_splits)} sub-texts.")
        
        return all_splits
    
    # def create_Documents_from_news(self, result):
    def create_Documents_from_news(self, news):
        # split text.
        chunks = self.split_text_from_news(text=news.content)
        
        # prepare splited documents from chunks.
        splited_documents = []
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "news_id": news.news_id, #
                    "title": news.title, #
                    "published_date": news.published_date, #
                    "published_time": news.published_time, #
                    "source_url": news.source_url, #
                    "chunk_index": i,
                    "total_chunks": len(chunks), #
                    }, 
                id=f"{id}#chunk={i}"
                )
            splited_documents.append(doc)
        self.logger.info(f"{DocumentProcessor.__name__}: Total {len(splited_documents)} splited documents for press release (title: {news.title}) - id: {news.news_id} were created.")
        
        return splited_documents
    
   