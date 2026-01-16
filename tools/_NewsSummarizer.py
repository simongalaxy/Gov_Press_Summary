from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

# from Grok.com

class NewsSummarizer:
    def __init__(self, logger):
        self.logger = logger
        self.modelName = os.getenv("OLLAMA_SUMMARIZATION_MODEL")
        self.llm = ChatOllama(
            model=self.modelName, 
            temperature=0.1
        )
        self.summary_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a concise government press release summarizer."),
            ("human", "Summarize the following press release within 200 words maximum if possible, "
                    "focusing on topic, key decisions/announcements, impact, keywords and quotes if relevant.\n\n{content}")
        ])
        self.chain = self.summary_prompt | self.llm | StrOutputParser()

    # Batch version
    async def summarize_batch(self, chunks): 
        async def safe_invoke(chunk): 
            try: 
                return await self.chain.ainvoke({"content": chunk}) 
            except Exception as e: 
                self.logger.error("Error summarizing chunk: %s", e) 
                return None 
            
        tasks = [safe_invoke(chunk) for chunk in chunks] 
        results = await asyncio.gather(*tasks) 
        
        for i, r in enumerate(results): 
            self.logger.info("Chunk %d summary:\n%s", i, r) 
        
        return results