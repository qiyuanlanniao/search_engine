# -*- coding:utf-8 -*-

from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from search.views import SearchSuggest, SearchView,IndexView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name="index"),
    path('suggest/', SearchSuggest.as_view(), name="suggest"),
    path('search/', SearchView.as_view(), name="search")
]

