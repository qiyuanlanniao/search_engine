# -*- coding:utf-8 -*-
import re

import redis
import scrapy
from scrapy.loader import ItemLoader
from w3lib.html import remove_tags
from elasticsearch_dsl.connections import connections
from itemloaders.processors import Join, MapCompose, TakeFirst, Identity

from ArticleSpider.models.es_types import ArticleType

es = connections.create_connection(ArticleType._doc_type.using)

redis_cli = redis.StrictRedis(host="localhost")


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def date_convert(value):
    match_re = re.match(".*?(\d+.*)", value)
    if match_re:
        return match_re.group(1)
    else:
        return "1970-07-01"


def gen_suggests(index, info_tuple):
    # 根据字符串生成搜索建议数组
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            # 调用es的analyze接口分析字符串
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter': ["lowercase"]}, body=text)
            analyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"]) > 1])
            new_words = analyzed_words - used_words
        else:
            new_words = set()

        if new_words:
            suggests.append({"input": list(new_words), "weight": weight})

    return suggests


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class JobBoleArticleItem(scrapy.Item):
    # 定义需要爬取的字段
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=Identity()
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    fav_nums = scrapy.Field()
    tags = scrapy.Field(
        output_processor=Join(separator=",")
    )
    content = scrapy.Field()

    def save_to_es(self):
        # 创建一个ArticleType实例，将爬取到的数据映射到Elasticsearch的数据模型
        article = ArticleType()
        # 将Item字段映射到ArticleType的属性
        article.title = self['title']
        article.create_date = self['create_date']
        article.content = remove_tags(self["content"])
        article.front_image_url = self["front_image_url"]
        if "front_image_path" in self:
            article.front_image_path = self["front_image_path"]
        article.praise_nums = self["praise_nums"]
        article.fav_nums = self["fav_nums"]
        article.comment_nums = self["comment_nums"]
        article.url = self["url"]
        article.tags = self["tags"]
        article.meta.id = self["url_object_id"]
        # 使用gen_suggests函数生成搜索建议
        article.suggest = gen_suggests(ArticleType._doc_type.index, ((article.title, 10), (article.tags, 7)))
        # 将ArticleType实例保存到Elasticsearch
        article.save()
        # 在Redis中增加计数
        redis_cli.incr("jobbole_count")

        return
