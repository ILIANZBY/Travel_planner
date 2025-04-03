import sys
import os
import json
import tempfile
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# 添加 Scrapy 项目路径

script_dir = os.path.dirname(os.path.abspath(__file__))

#project_path = os.path.join(script_dir, '..', 'attraction')
project_path = os.path.join(script_dir, '..')

sys.path.append(project_path)

# 导入爬虫类

from attraction.attraction.spiders.ctrip import AttractionSpider
from attraction.attraction.pipelines import JsonWriterPipeline
      
def GetAttractionData(queue):
    """
    封装 Scrapy 爬虫为一个工具函数，返回抓取的数据（JSON 格式）。
    """
    # 初始化 CrawlerProcess，加载 Scrapy 项目的配置
    process = CrawlerProcess(get_project_settings())


    # 动态添加自定义 Pipeline
    process.settings.set("ITEM_PIPELINES", {
        #"__main__.JsonWriterPipeline": 1,  # 使用当前脚本中的 Pipeline
        "attraction.attraction.pipelines.JsonWriterPipeline": 1, # 使用 attraction.pipelines 中的 Pipeline
    })

    # 创建一个临时文件用于存储爬虫的结果
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
        output_file_path = temp_file.name

    # 配置 Scrapy 输出到临时文件
    process.settings.set('FEEDS', {output_file_path: {'format': 'json'}})

    # 运行爬虫
    process.crawl(AttractionSpider)
    process.start()  # 启动爬虫

    # 将临时文件路径放入队列
    queue.put(output_file_path)

# 示例调用
if __name__ == "__main__":
    data = GetAttractionData()
    print(json.dumps(data, indent=4, ensure_ascii=False))