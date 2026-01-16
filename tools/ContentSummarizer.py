from langchain_ollama import OllamaLLM
from langchain_classic.chains.summarize import load_summarize_chain
from langchain_community.docstore.document import Document
from langchain_core.prompts import PromptTemplate

from pprint import pformat
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

class ContentSummarizer:
    def __init__(self, logger):
        self.logger = logger 
        self.modelName = os.getenv("OLLAMA_SUMMARIZATION_MODEL")
        self.llm = OllamaLLM(
            model=self.modelName,
            temperature=0.15
        )
        self.chain = load_summarize_chain(
            llm=self.llm, 
            chain_type='stuff'
        )

    async def summarize_content(self, splited_doc_list):
        tasks = [self.chain.ainvoke(doc) for doc in splited_doc_list]
        summaries = await asyncio.gather(*tasks)
        
        self.logger.info(f"Total Summaries generated: {len(summaries)}")
        
        for i, summary in enumerate(summaries):
            self.logger.info(f"No. {i} - Summary: \n%s", pformat(summary, indent=2))
        
        return summaries