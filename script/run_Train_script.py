import sys
import os
import json
from datetime import datetime, timedelta
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import tempfile

# 添加 Scrapy 项目路径
script_dir = os.path.dirname(os.path.abspath(__file__))

project_dir = os.path.join(script_dir, '..')

sys.path.append(project_dir)

# 导入爬虫类
from train.train.spiders.ctrip import TrainSpider
from train.train.pipelines import JsonWriterPipeline

        
def GetTrainData(dStation, aStation, travelDate, queue):
    """
    封装 Scrapy 爬虫为一个工具函数，返回抓取的数据（JSON 格式）。
    """

    process = CrawlerProcess(get_project_settings())

    # 动态添加自定义 Pipeline
    process.settings.set("ITEM_PIPELINES", {
        "train.train.pipelines.JsonWriterPipeline": 1,  # 使用当前脚本中的 Pipeline
    })

    # 创建一个临时文件用于存储爬虫的结果
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
        output_file_path = temp_file.name
    
    # 配置 Scrapy 输出到临时文件
    process.settings.set('FEEDS', {output_file_path: {'format': 'json'}})

    # 启动爬虫
    process.crawl(TrainSpider, dStation=dStation, aStation=aStation, travelDate=travelDate)
    process.start()


    # 将临时文件路径放入队列
    queue.put(output_file_path)

# 示例调用
if __name__ == "__main__":
     # 提供出发站和到达站作为参数
    departure_station = "广州"
    arrival_station = "长沙"

    travelDate=(datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d')
    data = GetTrainData(departure_station, arrival_station, travelDate)
    print(json.dumps(data, indent=4, ensure_ascii=False))