from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, BrowserConfig, MemoryAdaptiveDispatcher
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling.filters import URLPatternFilter, FilterChain

from pprint import pformat
import asyncio
import os
import re
from dotenv import load_dotenv
load_dotenv()


class WebCrawler:
    def __init__(self, logger):
        self.logger = logger
        self.url_filter = URLPatternFilter(patterns=[r"^https:\/\/www\.info\.gov\.hk\/gia\/general\/\d{6}\/\d{2}\/P\d+\.htm$"])
        self.filter_chain = FilterChain(filters=[self.url_filter])
        self.browser_config = BrowserConfig(
            headless=True,
            text_mode=True,
            )
        self.deep_crawl_strategy = BFSDeepCrawlStrategy(
                max_depth=1,  # Reduced depth for faster crawling
                include_external=False,
                filter_chain=self.filter_chain
                )
        self.crawl_config = CrawlerRunConfig(
            deep_crawl_strategy=self.deep_crawl_strategy,
            scraping_strategy=LXMLWebScrapingStrategy(),
            exclude_all_images=True,
            exclude_social_media_domains=True,
            exclude_external_links=True,
            target_elements=['div[id="PRHeadline"]', 'span[id="pressrelease"]'],
            cache_mode=CacheMode.BYPASS
            )
        self.dispatcher = MemoryAdaptiveDispatcher(
            memory_threshold_percent=75.0,
            max_session_permit=20
        )
        self.logger.info(f"Class - {WebCrawler.__name__} initiated.")

    
    async def crawl_date_page(self, url: str):
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            self.logger.info(f"{WebCrawler.__name__}: Start crawl year page - {url} ...")
            results = await crawler.arun(
                url=url,
                config=self.crawl_config
            )
            
            return results
    
    
    async def fetch_all_news(self, urls: list[str]):
        self.logger.info(f"{WebCrawler.__name__}: Start fetch all news.")
        
        tasks = [self.crawl_date_page(url=url) for url in urls]
        results = await asyncio.gather(*tasks)     
        self.logger.info(f"{WebCrawler.__name__}: Total No. of year urls fetched: {len(urls)}")

        result_lists = self.consolidate_results(results=results)
        
        return result_lists
    
    
    def consolidate_results(self, results):
        results_lists = []
        for result in results:
            for item in result:
                if re.search(r"P.*\.htm", item.url): # to only get the result crawled from press release where its url with pattern starting with "P" and ending with ".htm".
                # if "press_" not in item.url:
                    results_lists.append(item)
                    self.logger.info(f"url: {item.url}")
                    self.logger.info(f"Content: \n%s", item.markdown)
                    self.logger.info("-"*50)
                
        self.logger.info(f"{WebCrawler.__name__}: Total No. of Press Release fetched: {len(results_lists)}.")    
        
        return results_lists # remove the first page.
    
