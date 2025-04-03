import sys
import os
import json
import argparse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# # 添加 Scrapy 项目路径
# sys.path.append("C:\\Users\\86177\\Desktop\\爬虫工具函数\\测试\\plane")

script_dir = os.path.dirname(os.path.abspath(__file__))

project_path = os.path.join(script_dir, '..', 'PlaneTest/plane')

sys.path.append(project_path)

# 导入爬虫类

from plane.spiders.ctrip import CtripSpider

# 用于存储抓取结果的列表
results = []

# 定义一个Pipeline，用于收集数据
class JsonWriterPipeline:
    def open_spider(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

    def close_spider(self, spider):
        spider.logger.info("Spider closed: %s" % spider.name)

    def process_item(self, item, spider):
        results.append(dict(item))  
        return item
        
def GetPlaneData(dStation, aStation):
    """
    封装 Scrapy 爬虫为一个工具函数,返回抓取的数据(JSON 格式)。
    """
    process = CrawlerProcess(get_project_settings())

    process.settings.set("ITEM_PIPELINES", {
        "__main__.JsonWriterPipeline": 1,  
    })

    # 运行爬虫
    process.crawl(CtripSpider, dStation=dStation, aStation=aStation)
    process.start()  

    return results

# 示例调用
if __name__ == "__main__":
     # 提供出发站和到达站作为参数
    
    # parser = argparse.ArgumentParser(description="Run Ctrip Spider with specified stations.")
    # parser.add_argument('dStation', type=str, help='Departure Station')
    # parser.add_argument('aStation', type=str, help='Arrival Station')
    
    # args = parser.parse_args()

    # departure_station = args.dStation
    # arrival_station = args.aStation
    
    # data = scrape_ctrip_data(departure_station, arrival_station)

    data = GetPlaneData('广州', '秦皇岛')

    print(json.dumps(data, indent=4, ensure_ascii=False))