from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from pydantic import BaseModel, Field
from typing import List, Optional

from datetime import date, time
from pprint import pformat
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

class News(BaseModel):
    publish_dept: str = Field(description="Department published the press release.")
    publish_date: date = Field(description="Date published the press release.")
    publish_time: time = Field(description="Time published the press release.")
    title: str = Field(description="Title of the press release.")
    keywords: List[str] = Field(description="content keywords.")


class NewsSummarizer:
    def __init__(self, logger):
        self.logger = logger
        self.modelName = os.getenv("OLLAMA_SUMMARIZATION_MODEL")
        self.llm = ChatOllama(
            model=self.modelName,
            temperature=0.1
        )
        self.structured_llm = self.llm.with_structured_output(News)
        self.prompt_template = PromptTemplate.from_template(
        """Extract the information from the following content:\n {content}.  
        Only extract the properties mentioned in 'News' function.
        Only use the information from the content.
        """
        )
        self.logger.info(f"{NewsSummarizer.__name__} initiated.")
    
    
    def log_summaries(self, summaries) -> None:
        for i, summary in enumerate(summaries):
            self.logger.info(f"Summary No {i}: ")
            self.logger.info(pformat(summary, indent=2))
            self.logger.info("-"*50)
             
        return 
    
    
    async def summarize_all_news(self, news_list):
        self.logger.info("Start Summarization.")
        tasks  = [self.structured_llm.ainvoke(self.prompt_template.format(content=news.markdown)) for news in news_list]
        responses = await asyncio.gather(*tasks)
        summaries = [response.model_dump_json() for response in responses]
        self.log_summaries(summaries=summaries)
        
        self.logger.info("summarization end.")
        
        return summaries