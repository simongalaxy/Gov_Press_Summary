from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from tools.PostgresDatabase import PostgresDBHandler

import asyncio
from pprint import pformat
import json
import os
from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel, Field
from typing import List, Optional


class Summary(BaseModel):
    summary: str = Field(description="summary of the press release")
    keyword: List[str] = Field(description="keyword of the press release")


class NewsSummarizer:
    def __init__(self, logger, PsqlHandler: PostgresDBHandler):
        self.logger = logger
        self.DBhandler = PsqlHandler
        self.modelName = os.getenv("OLLAMA_SUMMARIZATION_MODEL")
        self.llm = ChatOllama(
            model= self.modelName,
            temperature=0.1
            )
        self.structured_llm = self.llm.with_structured_output(Summary)
        self.prompt = PromptTemplate.from_template(
            "Summarize the following content and the keywords of the content:\n{job_content}. Do not add interpretations, Do not invent details. Only use information from the content."
        )
        self.logger.info("NewsSummarizer has been initiatied.")


    # Extract structured job data from unstructured job description using LLM/    
    async def summarize_news(self, news, keyword):
        
        # get the job summary.
        summary = await self.structured_llm.ainvoke(
            self.prompt.format(job_content=news.content)
        )
        
        # convert pydantic class to dict.
        summary_dict = summary.model_dump()
        # summary_dict = job.id
        # update relevant data in postgresql database.
        self.DBhandler.update_JobAd(id=news.id, update_data=summary_dict)
        
        self.logger.info(f"Original news content:\n {news.content}")
        self.logger.info(f"Extracted news info (data type: {type(summary_dict)}): \n%s", pformat(summary_dict, indent=2))
        self.logger.info("-"*100)
          
        return summary_dict
    
    
    async def summarize_all_jobs(self, news_list):
        self.logger.info("News Summarization starts.")
        tasks = [self.summarize_news(news=news) for news in news_list]
        summaries = await asyncio.gather(*tasks)
        self.logger.info("News summarization completed.")
        
        return summaries
        
