from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, BrowserConfig, MemoryAdaptiveDispatcher
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy

import datetime
import calendar
import asyncio
from pprint import pprint
import re


class WebCrawler:
    def __init__(self, logger):
        self.logger = logger
        self.browser_config = BrowserConfig(
            headless=True,
            text_mode=True
        )
        self.crawl_config_NewsPage = CrawlerRunConfig(
            scraping_strategy=LXMLWebScrapingStrategy(),
            exclude_all_images=True,
            exclude_social_media_domains=True,
            exclude_external_links=True,
            # Use valid CSS attribute selectors for better compatibility
            target_elements=['div[id="PRHealine"]', 'span[id="pressrelease"]'], # for pres release content.
            cache_mode=CacheMode.BYPASS,
        )
        self.crawl_config_DatePage = CrawlerRunConfig(
            scraping_strategy=LXMLWebScrapingStrategy(),
            exclude_all_images=True,
            exclude_social_media_domains=True,
            exclude_external_links=True,
            cache_mode=CacheMode.BYPASS,
        )
        self.dispatcher = MemoryAdaptiveDispatcher(
            memory_threshold_percent=70,
            check_interval=1,
            max_session_permit=3
        )
        
        self.logger.info(f"{WebCrawler.__name__} initiated.")


    async def crawl_news_pages(self, urls: list[str]):
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            news_results = await crawler.arun_many(
                urls=urls, 
                config=self.crawl_config_NewsPage,
                dispatcher=self.dispatcher
            )
        self.logger.info(f"Total {len(news_results)} press release pages crawled.")
        for news in news_results:
            self.logger.info(f"url: {news.url}")
            self.logger.info("Press releaase: \n%s", news.markdown)
            self.logger.info("-"*50)
              
        return news_results
    
    
    async def crawl_date_pages(self, urls: list[str]):
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            results = await crawler.arun_many(
                urls=urls, 
                config=self.crawl_config_DatePage,
                dispatcher=self.dispatcher
            )
        
        # extract the job page links.
        news_links = []
        for i, result in enumerate(results):
            links = result.links.get("internal", [])
            for link in links:
                if re.search(pattern=r"P.*\.htm", string=link["href"]):
                    news_links.append(link["href"])
                    
        self.logger.info(f"Total {len(news_links)} press release page links crawled from {len(urls)} date pages.")    
         
        return news_links


    def generate_urls(self, year: int, month: int) -> list[str]:
        num_days = calendar.monthrange(year, month)[1]
        dates = [datetime.date(year, month, day).strftime("%Y%m%d") for day in range(1, num_days + 1)]
        urls = [f"https://www.info.gov.hk/gia/general/{date[:-2]}/{date[-2:]}.htm" for date in dates]
        for i, url in enumerate(urls):
            self.logger.info(f"{i}: {url}")
        
        return urls


    def crawl_all_news_pages(self, year: int, month: int): 
        # Generate search pages.
        urls = self.generate_urls(
            year=year, 
            month=month
        )

        # crawl all links for job pages from search pages.
        news_links = asyncio.run(self.crawl_date_pages(urls=urls))
        
        # crawl all contents from each job pages.
        news_results = asyncio.run(self.crawl_news_pages(urls=news_links))

        return news_results
        
        
