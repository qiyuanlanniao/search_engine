# -*- coding:utf-8 -*-

import time
import re
import json
from urllib import parse

import scrapy
from scrapy import Request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from ArticleSpider.items import JobBoleArticleItem, ArticleItemLoader
from ArticleSpider.utils.common import get_md5

# 配置 Chrome WebDriver 的服务
service = Service(r'C:\Users\启元\Desktop\综合课设II_自然语言处理\搜索引擎\chromedriver-win64\chromedriver.exe')


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['news.cnblogs.com']
    start_urls = ['https://news.cnblogs.com/']

    # 处理 HTTP 状态码为 404 的情况
    handle_httpstatus_list = [404]

    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fail_urls = []  # 存储请求失败的 URL
        self.username = 'hmca'
        self.password = 'KaoYanqinghua99@'

    def start_requests(self):
        cookies = []
        browser = webdriver.Chrome(service=service)

        # 使用 Selenium 模拟登录获取 Cookies
        url = 'https://news.cnblogs.com/'
        browser.get(url)
        browser.find_element(By.CSS_SELECTOR, '#login_area > a:nth-child(1)').click()
        time.sleep(2)
        browser.execute_script("Object.defineProperties(navigator,{webdriver:{get:()=>undefined}})")
        browser.find_element(By.CSS_SELECTOR, 'input[formcontrolname="username"]').send_keys(self.username)
        time.sleep(1)
        browser.find_element(By.CSS_SELECTOR, 'input[formcontrolname="password"]').send_keys(self.password)
        time.sleep(3)
        browser.find_element(By.CSS_SELECTOR, 'button').click()
        time.sleep(2)
        browser.find_element(By.CSS_SELECTOR, '.sm-btn.sm-btn-default').click()
        time.sleep(2)

        # 获取登录后的 Cookies
        cookies = browser.get_cookies()
        cookies_dict = {}
        for cookie in cookies:
            cookies_dict[cookie['name']] = cookie['value']

        # 发送请求，并将 Cookies 附加到请求中
        for url in self.start_urls:
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            yield Request(url, headers=headers, cookies=cookies_dict, callback=self.parse)

    def parse(self, response, **kwargs):
        # 处理请求失败的情况
        if response.status == 404:
            self.fail_urls.append(response.url)
            self.crawler.stats.inc_value("failed_url")

        # 解析列表页，提取文章信息
        post_nodes = response.css('#news_list .news_block')
        for post_node in post_nodes:
            image_url = post_node.css('.entry_summary a img::attr(src)').extract_first("")
            if image_url.startswith("//"):
                image_url = "https:" + image_url
            post_url = post_node.css('h2 a::attr(href)').extract_first("")

            # 发送请求，解析详情页
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url},
                          callback=self.parse_detail)

        # 获取下一页的 URL，并发送请求
        next_url = response.xpath("//a[contains(text(),'Next >')]/@href").extract_first("")
        yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        # 从 URL 中提取文章 ID
        match_re = re.match(".*?(\d+)", response.url)
        if match_re:
            post_id = match_re.group(1)

            # 使用 ItemLoader 进行数据加载和预处理
            item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
            item_loader.add_css("title", "#news_title a::text")
            item_loader.add_css("create_date", "#news_info .time::text")
            item_loader.add_css("content", "#news_content")
            item_loader.add_css("tags", ".news_tags a::text")
            item_loader.add_value("url", response.url)
            if response.meta.get("front_image_url", []):
                item_loader.add_value("front_image_url", response.meta.get("front_image_url", []))

            # 发送请求，解析文章相关的数据（如点赞数、收藏数、评论数）
            yield Request(url=parse.urljoin(response.url, "/NewsAjax/GetAjaxNewsInfo?contentId={}".format(post_id)),
                          meta={"article_item": item_loader, "url": response.url}, callback=self.parse_nums)

    def parse_nums(self, response):
        # 解析 Ajax 响应，获取文章的相关数据
        j_data = json.loads(response.text)
        item_loader = response.meta.get("article_item", "")

        # 添加点赞数、收藏数、评论数等数据到 ItemLoader
        item_loader.add_value("praise_nums", j_data["DiggCount"])
        item_loader.add_value("fav_nums", j_data["TotalView"])
        item_loader.add_value("comment_nums", j_data["CommentCount"])
        item_loader.add_value("url_object_id", get_md5(response.meta.get("url", "")))

        # 使用 ItemLoader 加载数据到 Item 对象
        article_item = item_loader.load_item()

        # 返回 Item 对象
        yield article_item
