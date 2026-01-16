from tools.logger import Logger
from tools.webCrawler import WebCrawler
from tools.SQLiteDatabase import sqliteHandler, News
from tools.DocumentProcessor import DocumentProcessor
from tools.ChromaDBHandler import ChromaDBHandler
# from tools.ContentSummarizer import ContentSummarizer
# from tools.NewsSummarizer import NewsSummarizer

import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

import datetime
import calendar

def generate_urls(year: int, month: int) -> list[str]:
    
    num_days = calendar.monthrange(year, month)[1]
    dates = [datetime.date(year, month, day).strftime("%Y%m%d") for day in range(1, num_days + 1)]
    urls = [f"https://www.info.gov.hk/gia/general/{date[:-2]}/{date[-2:]}.htm" for date in dates]
    
    return urls
    

def main():
    
    # initiate classes.
    logger = Logger(__name__).get_logger()
    crawler = WebCrawler(logger=logger)
    sqlDBHandler = sqliteHandler(logger=logger)
    sqlDBHandler.check_and_create_table()
    docProcessor = DocumentProcessor(logger=logger)
    chromaDBHandler = ChromaDBHandler(logger=logger)
    # summarizer = ContentSummarizer(logger=logger)
    # summarizer = NewsSummarizer(logger=logger)
    
    # generate urls by dates.
    year = 2025
    month = 11
    urls = generate_urls(
        year=year,
        month=month
    )
    logger.info(f"Years: {year}, Month: {month}")
    logger.info(f"Total No. of urls: {len(urls)}")
    
    # crawl all press release.
    results_list = asyncio.run(crawler.fetch_all_news(urls=urls))
    
    # save results into News and then create splitted documents for text summarization and saving to chromadb and then sqlitedb.

    for result in results_list:
        news_entry = News(
            news_id=result.url.split("/")[-1].replace(".htm", ""),
            title=result.metadata["title"],
            published_date=result.markdown.split("\n")[-4].split(", ", 1)[-1].strip(),
            published_time=result.markdown.split("\n")[-3].split(" ")[-2],
            source_url=result.url,
            content=result.markdown
        )
        
        # save to chromadb.
        splitted_dococuments = docProcessor.create_Documents_from_news(news=news_entry)
        news_entry.total_chunks = len(splitted_dococuments)
        chromaDBHandler.add_splits_to_db(documents=splitted_dococuments)

        # save to sqlitedb.
        sqlDBHandler.create_news(news_item=news_entry)
    
    return
        
        
        


if __name__ == "__main__":
    main()
