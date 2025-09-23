# -*- coding:utf-8 -*-

import json
from datetime import datetime

import redis
from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponse
from elasticsearch import Elasticsearch

from search.models import ArticleType

client = Elasticsearch(hosts=["127.0.0.1"])
redis_cli = redis.StrictRedis()


class IndexView(View):
    # 首页
    def get(self, request):
        topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
        topn_search = [item.decode('utf-8') for item in topn_search]
        return render(request, "index.html", {"topn_search": topn_search})


class SearchSuggest(View):
    def get(self, request):
        key_words = request.GET.get('s', '')
        re_datas = []
        if key_words:
            s = ArticleType.search()
            s = s.suggest('my-suggest', key_words, completion={
                "field": "suggest", "fuzzy": {
                    "fuzziness": 2
                },
                "size": 10
            })
            suggestions = s.execute()
            for match in getattr(suggestions.suggest, "my-suggest")[0].options:
                source = match._source.title
                re_datas.append(source)
        return HttpResponse(json.dumps(re_datas), content_type="application/json")


def process_content(content, max_len):
    import re
    # 因为暴力截断content导致html标签错乱
    rtn_content = content
    keyword = ""
    searchObj = re.search(r'<span class="keyWord">(.*?)</span>', content, re.M | re.I)
    if searchObj:
        keyword = searchObj.group()

    if keyword:
        datas = re.split('<span class="keyWord">.*?</span>', content)
        hasLen = 0
        index = 0
        for i, data in enumerate(datas):
            hasLen += len(data)
            index += 1
            if hasLen > max_len:
                break
        if datas[:index]:
            rtn_content = '<span class="keyWord">{}</span>'.format(keyword).join(datas[:index])
    return rtn_content


class SearchView(View):
    def get(self, request):
        key_words = request.GET.get("q", "")
        # 热门搜索排名
        redis_cli.zincrby("search_keywords_set", 1, key_words)  # 将关键词保存到内存中

        topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
        topn_search = [item.decode('utf-8') for item in topn_search]
        # 分页跳转
        page = request.GET.get("p", "1")
        page = int(page)
        try:
            page = int(page)
        except:
            page = 1
        # redis传递值
        jobbole_count = redis_cli.get("jobbole_count")
        jobbole_count = int(jobbole_count.decode('utf-8'))
        start_time = datetime.now()
        response = client.search(
            index="jobbole",
            body={
                "query": {
                    "multi_match": {
                        "query": key_words,
                        "fields": ["tags", "title", "content", "job_desc"]
                    }
                },
                # 分页：有了page可以调用from、size
                "from": (page - 1) * 10,
                "size": 10,
                "highlight": {
                    "pre_tags": ['<span class="keyWord">'],
                    "post_tags": ['</span>'],
                    "fields": {
                        "title": {},
                        "content": {},
                    }
                }
            }
        )
        end_time = datetime.now()
        last_seconds = (end_time - start_time).total_seconds()
        total_nums = response["hits"]["total"]
        if (page % 10) > 0:
            page_nums = int(total_nums / 10 + 1)
        else:
            page_nums = int(total_nums / 10)
        hit_list = []
        for hit in response["hits"]["hits"]:
            hit_dict = {}
            if "title" in hit["highlight"]:
                hit_dict["title"] = "".join(hit["highlight"]["title"])
            else:
                hit_dict["title"] = hit["_source"]["title"]
            if "content" in hit["highlight"]:
                hit_dict["content"] = "".join(hit["highlight"]["content"])
            else:
                hit_dict["content"] = hit["_source"]["content"]
            hit_dict["content"] = process_content(hit_dict["content"], 400)
            hit_dict["create_date"] = hit["_source"]["create_date"]
            hit_dict["url"] = hit["_source"]["url"]
            hit_dict["score"] = hit["_score"]

            hit_list.append(hit_dict)
        return render(request, "result.html", {
            # 分页：传递总数和page
            "total_nums": total_nums,
            "page": page,
            "all_hits": hit_list,
            "key_words": key_words,
            "page_nums": page_nums,
            "last_seconds": last_seconds,
            "jobbole_count": jobbole_count,
            "topn_search": topn_search
        })

