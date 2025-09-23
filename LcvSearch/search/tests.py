# -*- coding:utf-8 -*-
from search.models import ArticleType

s = ArticleType.search()
s = s.suggest('my-suggest', "苹果", completion={
    "field": "suggest", "fuzzy": {
        "fuzziness": 2
    },
    "size": 10
})

suggestions = s.execute()

for match in getattr(suggestions.suggest, "my-suggest")[0].options:
    source = match._source.title

