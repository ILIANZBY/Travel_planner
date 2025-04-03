import sys
import os
import json
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# # 添加 Scrapy 项目路径
# sys.path.append("C:\\Users\\86177\\Desktop\\爬虫工具函数\\测试\\plane")

script_dir = os.path.dirname(os.path.abspath(__file__))

project_path = os.path.join(script_dir, '..', '测试\\plane')

sys.path.append(project_path)

# 导入爬虫类

from plane.spiders.ctrip import CtripSpider

# 用于存储抓取结果的列表
results = []

# 定义一个简单的 Pipeline，用于收集数据
class JsonWriterPipeline:
    def open_spider(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

    def close_spider(self, spider):
        spider.logger.info("Spider closed: %s" % spider.name)

    def process_item(self, item, spider):
        results.append(dict(item))  # 将抓取的数据添加到 results 列表
        return item
        
def scrape_ctrip_data(dStation, aStation):
    """
    封装 Scrapy 爬虫为一个工具函数，返回抓取的数据（JSON 格式）。
    """
    # 初始化 CrawlerProcess，加载 Scrapy 项目的配置
    process = CrawlerProcess(get_project_settings())


    # 动态添加自定义 Pipeline
    process.settings.set("ITEM_PIPELINES", {
        "__main__.JsonWriterPipeline": 1,  # 使用当前脚本中的 Pipeline
    })

    # 运行爬虫
    process.crawl(CtripSpider, dStation=dStation, aStation=aStation)
    process.start()  # 启动爬虫

    # 返回抓取结果
    return results

# 示例调用
if __name__ == "__main__":
     # 提供出发站和到达站作为参数
    departure_station = "秦皇岛"
    arrival_station = "上海"
    data = scrape_ctrip_data(departure_station, arrival_station)
    print(json.dumps(data, indent=4, ensure_ascii=False))