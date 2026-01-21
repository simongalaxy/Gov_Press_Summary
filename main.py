from tools.logger import Logger
from tools.webCrawler import WebCrawler
from tools.PostgresDatabase import PostgresDBHandler
from tools.DocumentProcessor import DocumentProcessor
from tools.ChromaDBHandler import ChromaDBHandler
# from tools.ContentSummarizer import ContentSummarizer

from pprint import pformat
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()


# main program.
def main():
    
    # initiate classes.
    logger = Logger(__name__).get_logger()
    crawler = WebCrawler(logger=logger)
    PsqlHandler = PostgresDBHandler(logger=logger)
    PsqlHandler.check_and_create_table()
    docProcessor = DocumentProcessor(logger=logger)
    chromaDBHandler = ChromaDBHandler(logger=logger)
    # summarizer = ContentSummarizer(logger=logger)

    
    # generate urls by dates.     # Format: startDate = "20251011", endDate = "20251231"
    startDate = "20251230"
    endDate = "20251231"
    
    # crawl all press release.
    news_list = asyncio.run(crawler.crawl_all_news_pages(startDate=startDate, endDate=endDate))
    
    # save results into News and then create splitted documents for text summarization and saving to chromadb and then sqlitedb.
    PsqlHandler.save_news_to_db(news_list=news_list)
    
    news = PsqlHandler.list_all_News()
    for i, news_item in enumerate(news, start=1):
        logger.info(f"news_item No. {i}: {pformat(news_item.model_dump())}")
        logger.info("-"*40)
    
    # for result in results_list:
        
    #     # save to chromadb.
    #     splitted_dococuments = docProcessor.create_Documents_from_news(news=news_entry)
    #     news_entry.total_chunks = len(splitted_dococuments)
    #     chromaDBHandler.add_splits_to_db(documents=splitted_dococuments)

    #     # save to sqlitedb.
    #     sqlDBHandler.create_news(news_item=news_entry)
    
    return
        
        
        


if __name__ == "__main__":
    main()
