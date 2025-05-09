#!/usr/bin/env python3
"""
Single-file Scrapy crawler that:
 - Recursively crawls your domain
 - Downloads only OpenAI-supported file types
 - Honors download delays & AutoThrottle to avoid rate limits
 - Rotates User-Agents
 - Tracks metadata: original source page and preserves website path structure

Usage:
  pip install scrapy scrapy-user-agents
  python file_crawler.py

Outputs into ./data/files/<original-path>/filename
"""
import os
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.pipelines.files import FilesPipeline
from urllib.parse import urlparse

# Supported file extensions by OpenAI Vector Store
SUPPORTED_EXTENSIONS = {
    ".c", ".cpp", ".cs", ".css", ".doc", ".docx", ".go", ".html",
    ".java", ".js", ".json", ".md", ".pdf", ".php", ".pptx",
    ".py", ".rb", ".sh", ".tex", ".ts", ".txt"
}

class FileItem(scrapy.Item):
    file_urls = scrapy.Field()
    files = scrapy.Field()
    source_page = scrapy.Field()   # page where link was found

class CustomFilesPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        # preserve website path structure under data/files
        parsed = urlparse(request.url)
        # remove leading slash
        path = parsed.path.lstrip('/')
        # if path ends with slash, use default name
        if path.endswith('/') or not os.path.basename(path):
            filename = os.path.basename(parsed.netloc)
            path = os.path.join(path, filename)
        return path

class FileSpider(scrapy.Spider):
    name = "file_spider"
    start_urls = [os.getenv('START_URL', 'https://cob.org')]
    allowed_domains = [urlparse(start_urls[0]).netloc]

    custom_settings = {
        # Use our custom pipeline
        'ITEM_PIPELINES': {'__main__.CustomFilesPipeline': 1},
        'FILES_STORE': 'data/files',
        'FILES_EXPIRES': 0,
        # ---- Throttle & Retry ----
        "DOWNLOAD_DELAY": 2.0,                # 2s between requests
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 2.0,
        "AUTOTHROTTLE_MAX_DELAY": 30.0,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 0.5,
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 5,
        "RETRY_HTTP_CODES": [429, 403, 500, 502, 503, 504],
        # Rotate user agents
        'DOWNLOADER_MIDDLEWARES': {
            # disable built-in UA middleware
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            # enable fake-useragent middleware (install with pip install scrapy-fake-useragent)
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
        },
        # Logging
        'LOG_LEVEL': 'INFO',
    }

    def parse(self, response):
        # follow links and download supported files
        for href in response.css('a::attr(href)').getall():
            full_url = response.urljoin(href)
            parsed = urlparse(full_url)
            if parsed.netloc != self.allowed_domains[0]:
                continue

            path = parsed.path.lower()
            if any(path.endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                # capture the page where this file link was found
                yield FileItem(file_urls=[full_url], source_page=response.url)
            else:
                yield scrapy.Request(full_url, callback=self.parse)

if __name__ == '__main__':
    os.makedirs('data/files', exist_ok=True)
    process = CrawlerProcess()
    process.crawl(FileSpider)
    process.start()