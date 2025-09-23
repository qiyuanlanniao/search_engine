# 基于 Scrapy 的分布式新闻搜索引擎 🔎📰

一个集数据采集、处理、索引、检索与智能推荐于一体的高性能新闻搜索引擎。本项目通过 Scrapy 构建分布式异步爬虫集群，高效采集网络新闻（例如博客园），利用 Elasticsearch 构建强大的倒排索引及检索引擎，并通过 Django 框架搭建功能完善、交互友好的前后端应用，实现了亚秒级全文检索、智能搜索建议及热门趋势分析。


## 🌟 项目概览

本项目旨在构建一个从数据抓取到用户检索的全链路新闻搜索引擎。核心挑战包括大规模数据的分布式高效采集、动态网页内容处理、反爬虫策略应对、高性能检索引擎的构建与优化、以及用户友好的搜索体验设计。

该项目是作为“综合课设II”独立开发的，全面展示了在数据工程、后端开发和搜索技术方面的综合能力。

## ✨ 核心功能

*   **🚀 高效分布式爬虫集群：**
    *   基于 Scrapy 框架构建，支持分布式部署 (Scrapyd)。
    *   集成 Selenium 处理动态加载内容和模拟登录等反爬虫场景。
    *   实现高效数据采集（例如，>10000篇新闻，万页/10分钟的采集效率）。
*   **🔍 强大的检索引擎：**
    *   核心采用 Elasticsearch 构建倒排索引，支持海量数据存储与检索。
    *   自定义 ES 索引 (IK Analyzer) 以优化中文分词和检索效果。
    *   实现亚秒级全文检索、结果高亮、拼写纠错提示。
*   **💡 智能搜索体验：**
    *   集成实时搜索建议 (ES Suggest)。
    *   实现热门搜索排行 (Redis Sorted Set)。
    *   支持本地搜索历史记录。
*   **⚙️ 完整数据链路：**
    *   构建 ETL (Extract, Transform, Load) 管道，提升数据质量。
    *   数据从采集、清洗、结构化到索引的全流程管理。
*   **🖥️ 用户友好的前后端：**
    *   后端采用 Django (MVT) 框架提供核心 API 服务。
    *   前端使用 HTML5, CSS3, JavaScript, jQuery, AJAX 构建动态交互界面。
*   **📊 系统部署与监控：**
    *   利用 Scrapyd 实现爬虫的自动化部署与调度。
    *   结合 Kibana 进行数据可视化分析及系统性能监控。

## 🛠️ 技术栈

*   **后端 (Backend)：**
    *   Python 3.10
    *   Django (MVT)
    *   Scrapy (分布式爬虫框架)
    *   Elasticsearch (DSL, IK Analyzer) - 检索引擎
    *   Redis (缓存, 热门排行)
*   **前端 (Frontend)：**
    *   HTML5, CSS3
    *   JavaScript, jQuery, AJAX
*   **爬虫与数据处理 (Crawling & Data Processing)：**
    *   Selenium (处理动态网页)
*   **部署与监控 (Deployment & Monitoring)：**
    *   Scrapyd (Scrapy 部署与调度)
    *   Kibana (数据可视化与监控)
*   **开发工具 (Key Tools)：**
    *   PyCharm, Navicat

## 🏗️ 架构概览

系统主要由以下几个模块组成：

1.  **数据采集层 (Data Collection Layer)：**
    *   基于 Scrapy 的分布式爬虫集群。
    *   通过 Scrapyd 进行管理和调度。
    *   使用 Selenium 辅助处理动态内容。
2.  **数据处理与存储层 (Data Processing & Storage Layer)：**
    *   ETL 管道对原始数据进行清洗、转换和结构化。
    *   原始数据或中间数据可暂存（例如，数据库或文件系统）。
3.  **索引与检索层 (Indexing & Search Layer)：**
    *   Elasticsearch 作为核心检索引擎，构建倒排索引。
    *   IK Analyzer 用于中文分词优化。
    *   Redis 用于存储热门搜索、搜索建议等辅助数据。
4.  **应用服务层 (Application Service Layer)：**
    *   Django (MVT) 框架提供后端 API 接口，处理业务逻辑。
5.  **用户交互层 (User Interaction Layer)：**
    *   HTML/CSS/JS 构建的前端界面，与用户进行交互，展示搜索结果。
6.  **监控与管理层 (Monitoring & Management Layer)：**
    *   Kibana 对 Elasticsearch 中的数据进行可视化分析和监控。
    *   Scrapyd Web UI 监控爬虫状态。

## 🚀 快速开始

### 环境要求 (Prerequisites)

*   Python 3.10
*   Scrapy
*   Django
*   Elasticsearch 
*   IK Analyzer for Elasticsearch
*   Redis
*   Selenium 及对应浏览器驱动
*   Node.js 和 npm
*   Scrapyd

### 安装步骤 (Installation)

1.  **克隆仓库：**
    ```bash
    git clone https://github.com/你的用户名/你的搜索引擎仓库名.git
    cd 你的搜索引擎仓库名
    ```

2.  **创建并激活虚拟环境 (推荐)：**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows 系统: venv\Scripts\activate
    ```

3.  **安装 Python 依赖：**
    ```bash
    pip install -r requirements.txt
    ```
    (确保 `requirements.txt` 文件包含了所有必要的 Python 包)

4.  **安装 Elasticsearch 和 IK Analyzer：**
    *   请参照 Elasticsearch 官方文档安装 Elasticsearch。
    *   下载与您 Elasticsearch 版本对应的 IK Analyzer 插件，并解压到 Elasticsearch 的 `plugins` 目录下，重启 Elasticsearch。

5.  **安装 Redis：**
    *   请参照 Redis 官方文档进行安装。

6.  **配置项目：**
    *   **Django 设置：** 修改 `your_project_name/settings.py` (通常是 `settings.py`) 中的数据库配置 (如果除了 ES 和 Redis 之外还用了关系型数据库)、Elasticsearch 连接信息、Redis 连接信息等。
    *   **Scrapy 设置：** 检查 Scrapy 项目 (`scrapy_project_name/settings.py`) 中的 pipeline 配置，确保数据能正确写入 Elasticsearch。
    *   可能需要创建 `.env` 文件来管理敏感配置信息，并相应修改 `settings.py` 读取这些配置。

### 运行应用 (Running the Application)

1.  **启动 Elasticsearch 和 Redis 服务。**

2.  **运行数据库迁移 (如果使用 Django ORM 和关系型数据库)：**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

3.  **启动 Django 开发服务器：**
    ```bash
    python manage.py runserver
    ```
    应用通常可以在 `http://127.0.0.1:8000/` 访问。

4.  **运行 Scrapy 爬虫：**
    进入 Scrapy 项目目录 (`cd scrapy_project_name`):
    ```bash
    scrapy crawl your_spider_name
    ```
    或者通过 Scrapyd 进行部署和调度。

## 🎮 使用说明 (Usage)

*   打开浏览器访问 Django 应用的首页 (通常是 `http://127.0.0.1:8000/`)。
*   在搜索框中输入关键词进行新闻检索。
*   体验搜索建议、热门排行等功能。

<!-- ## 📁 项目结构 (可选, 但很有帮助)
