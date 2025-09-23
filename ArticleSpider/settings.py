# -*- coding:utf-8 -*-

import os
import random


BOT_NAME = 'ArticleSpider'

SPIDER_MODULES = ['ArticleSpider.spiders']
NEWSPIDER_MODULE = 'ArticleSpider.spiders'


# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 2

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = random.randint(1, 5)
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 1
CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

ITEM_PIPELINES = {
    # 'ArticleSpider.pipelines.ArticleImagePipeline': 1,
    # 'ArticleSpider.pipelines.JsonWithEncodingPipeline': 2,
    # 'ArticleSpider.pipelines.JsonExporterPipeline': 3,
    # 'ArticleSpider.pipelines.MysqlTwistedPipeline': 4,
    'ArticleSpider.pipelines.ElasticsearchPipeline': 5,
    # 'ArticleSpider.pipelines.ArticlespiderPipeline': 300,
}

IMAGES_URLS_FIELD = "front_image_url"
project_dir = os.path.dirname(os.path.abspath(__file__))
IMAGES_STORE = os.path.join(project_dir, 'images')

MYSQL_HOST = "192.168.174.129"
MYSQL_DBNAME = "article_spider"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"

SQL_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
SQL_DATE_FORMAT = "%Y-%m-%d"

USER = "19507370354"
PASSWORD = "kcsj123456789"
