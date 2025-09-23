# -*- coding:utf-8 -*-

import codecs
import json

from scrapy.exporters import JsonItemExporter
from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi
import MySQLdb
from MySQLdb.cursors import DictCursor


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    # 自定义json文件导出
    def __init__(self):
        self.file = codecs.open("article.json", "a", encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class MysqlPipeline(object):
    # 采用同步的机制写入mysql
    def __init__(self):
        self.conn = MySQLdb.connect("192.168.174.129", 'root', 'root', 'article_spider', charset="utf8",
                                    use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article(title,url,url_object_id,front_image_path,front_image_url,praise_nums,comment_nums,fav_nums,tags,content,create_date)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key update praise_nums=VALUES(praise_nums)
        """
        params = list()
        params.append(item.get("title", ""))
        params.append(item.get("url", ""))
        params.append(item.get("url_object_id", ""))
        params.append(item.get("front_image_path", ""))
        front_image = ",".join(item.get("front_image_url", []))
        params.append(front_image)
        params.append(item.get("praise_nums", 0))
        params.append(item.get("comment_nums", 0))
        params.append(item.get("fav_nums", 0))
        params.append(item.get("tags", ""))
        params.append(item.get("content", ""))
        params.append(item.get("create_date", "1970-07-01"))
        self.cursor.execute(insert_sql, tuple(params))
        self.conn.commit()

        return item


class MysqlTwistedPipeline(object):
    # 采用异步的机制写入mysql
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)
        return item

    def handle_error(self, failure, item, spider):
        print(failure)

    def do_insert(self, cursor, item):
        insert_sql = """
                    insert into jobbole_article(title,url,url_object_id,front_image_path,front_image_url,praise_nums,comment_nums,fav_nums,tags,content,create_date)
                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key update praise_nums=VALUES(praise_nums)
                """
        params = list()
        params.append(item.get("title", ""))
        params.append(item.get("url", ""))
        params.append(item.get("url_object_id", ""))
        params.append(item.get("front_image_path", ""))
        front_image = ",".join(item.get("front_image_url", []))
        params.append(front_image)
        params.append(item.get("praise_nums", 0))
        params.append(item.get("comment_nums", 0))
        params.append(item.get("fav_nums", 0))
        params.append(item.get("tags", ""))
        params.append(item.get("content", ""))
        params.append(item.get("create_date", "1970-07-01"))

        cursor.execute(insert_sql, tuple(params))


class JsonExporterPipeline(object):
    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        self.file.close()


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            image_file_path = ""
            for ok, value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path

        return item


class ElasticsearchPipeline(object):
    # 将数据写入到es中
    def process_item(self, item, spider):
        # 将item转换为es的数据
        item.save_to_es()
        return item
