# -*- coding: utf-8 -*-

# Scrapy settings for ctrip project
import os
import random

BOT_NAME = 'train'

SPIDER_MODULES = ['train.spiders']
NEWSPIDER_MODULE = 'train.spiders'

LOG_LEVEL = 'DEBUG'  # 日志级别，可选择 DEBUG, INFO, WARNING, ERROR, CRITICAL

# # 将日志输出到文件，而不是控制台
# LOG_FILE = 'scrapy.log'
# LOG_STDOUT = False

# # 完全禁用日志输出
# LOG_ENABLED = False

# 下载中间件配置
DOWNLOADER_MIDDLEWARES = {
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,  # 使用 scrapy-user-agents 插件
    # 'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,  # 禁用重试，防止循环请求
}

# 默认请求头配置
DEFAULT_REQUEST_HEADERS = {
   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
   'Accept-Language': 'en-US,en;q=0.5',
   'Accept-Encoding': 'gzip, deflate',
}

# 禁用 Cookies
COOKIES_ENABLED = False

# 设置导出的编码为 UTF-8，避免中文乱码
FEED_EXPORT_ENCODING = 'utf-8'

FEEDS = {
    'output.json': {
        'format': 'json',
        'encoding': 'utf-8',
        'indent': 4,  # 设置缩进，格式化 JSON
    },
}

# 配置下载延迟，模拟人类用户的行为，减缓爬取速度
#DOWNLOAD_DELAY = 4  # 每个请求之间的延迟时间（秒）
# 或者设置一个随机范围来随机化请求间隔
DOWNLOAD_DELAY = random.uniform(1, 3)

# 自动调节下载速度，根据当前服务器响应的情况调整爬虫的请求速率
AUTOTHROTTLE_ENABLED = True  # 启用自动调节下载速度
AUTOTHROTTLE_START_DELAY = 5  # 初始的延迟时间（秒）
AUTOTHROTTLE_MAX_DELAY = 30  # 最大的延迟时间（秒）
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0  # 目标并发请求数（控制每秒发出的请求数量）
AUTOTHROTTLE_DEBUG = True  # 启用调试输出

# 反爬策略，模拟人类访问，避免暴力抓取
# Randomize User-Agent（这是通过 `scrapy_user_agents` 插件实现的）

# 启用代理池（可选，提供 IP 代理池来随机化请求源，避免 IP 被封禁）
# DOWNLOADER_MIDDLEWARES.update({
#     'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 1,
# })
# HTTP_PROXY = 'http://your.proxy.server:port'
