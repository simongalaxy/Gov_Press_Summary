from tools.logger import Logger
from tools.webCrawler import WebCrawler
from tools.SQLiteDatabase import sqliteHandler, News
from tools.DocumentProcessor import DocumentProcessor
from tools.ChromaDBHandler import ChromaDBHandler
from tools.NewsSummarizer import NewsSummarizer

import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

def main():
    
    # initiate classes.
    logger = Logger(__name__).get_logger()
    crawler = WebCrawler(logger=logger)
    sqlDBHandler = sqliteHandler(logger=logger)
    sqlDBHandler.check_and_create_table()
    docProcessor = DocumentProcessor(logger=logger)
    chromaDBHandler = ChromaDBHandler(logger=logger)
    summarizer = NewsSummarizer(logger=logger)
    
    
    # generate urls by dates.
    urls = ["https://www.info.gov.hk/gia/general/202601/13.htm"]
    
    # crawl all press release.
    results_list = asyncio.run(crawler.fetch_all_news(urls=urls))
    
    # save results into News and then create splitted documents for text summarization and saving to chromadb and then sqlitedb.
    splited_doc_list = []
    for result in results_list:
        news_entry = News(
            news_id=result.url.split("/")[-1].replace(".htm", ""),
            title=result.metadata["title"],
            published_date=result.markdown.split("\n")[-4].split(", ", 1)[-1].strip(),
            published_time=result.markdown.split("\n")[-3].split(" ")[-2],
            source_url=result.url,
            content=result.markdown
        )

        # save splited documents to chromadb.
        splited_documents = docProcessor.create_Documents_from_news(news=news_entry)
        splited_doc_list.append(splited_documents)
        chromaDBHandler.add_splits_to_db(documents=splited_documents)
        
        # summary.
        summary = asyncio.run(summarizer.summarize_batch(chunks=splited_documents))
        
        # save news to sqliteDB.
        news_entry.total_chunks = len(splited_documents)
        # news_entry.summary = summary
        sqlDBHandler.create_news(news_item=news_entry)
        
        
        


if __name__ == "__main__":
    main()
