import scrapy
from datetime import datetime, timedelta
import re

class FindtripItem(scrapy.Item):
    TrainNumber = scrapy.Field()         
    DepartureTime = scrapy.Field()    
    OriginCity = scrapy.Field()
    ArrivalTime = scrapy.Field()
    DestCity = scrapy.Field()
    Price = scrapy.Field()
    Duration = scrapy.Field()          
    Distance = scrapy.Field()
    TrainDate = scrapy.Field()


class TrainSpider(scrapy.Spider):
    name = 'Ctrip'   #用命令行启动爬虫的名称
    allowed_domains = ['trains.ctrip.com']
    cities = [
        "北京", "上海", "成都", "广州", "天津", "青岛", 
        "深圳", "合肥", "重庆", "济南", "西安", "杭州",
        "沈阳", "长沙", "南京", "厦门", "武汉", "郑州", 
        
    ]

    results = []

    def __init__(self, dStation=None, aStation=None, travelDate=(datetime.now() + timedelta(days=6)).strftime('%Y-%m-%d'), *args, **kwargs):
        super(TrainSpider, self).__init__(*args, **kwargs)
        if not dStation or not aStation:
            raise ValueError("Both departure station (dStation) and arrival station (aStation) must be provided.")
        self.dStation = dStation
        self.aStation = aStation
        self.travelDate = travelDate
        now = datetime.now()
        self.six_days_later_str = (now + timedelta(days=6)).strftime('%Y-%m-%d')
    
    def start_requests(self):
       
        #base_url = f"https://trains.ctrip.com/webapp/train/list?ticketType=0&dStation={}&aStation={}&dDate={six_days_later_str}&rDate=&hubCityName=&highSpeedOnly=0"
        #url = base_url.format(self.dStation, self.aStation)
        url = f"https://trains.ctrip.com/webapp/train/list?ticketType=0&dStation={self.dStation}&aStation={self.aStation}&dDate={self.travelDate}&rDate=&trainsType=gaotie-dongche&hubCityName=&highSpeedOnly=0"

        self.logger.info(f"Generated URL: {url}")
        yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        
    
        # 保存页面 HTML 以供调试
        # with open("response.html", "w", encoding="utf-8") as f:
        #     f.write(response.text)

        # 定位到景点信息区域
        # trains = response.xpath('//div[@class="list-bd"]')
        # self.logger.info(f"Found {len(trains)} trains.")
        # if trains:
        #     first_train = trains[0]
        #     with open("FirstTrain.txt", "w", encoding="utf-8") as f:
        #         f.write(first_train.get())
        
        direct_trains = response.xpath('//div[@class="list-bd" and not(ancestor::div[contains(@class, "transfer-box")])]')
        self.logger.info(f"Found {len(direct_trains)} direct trains.")
        if direct_trains:
            first_train = direct_trains[0]
            # with open("FirstDirectTrain.txt", "w", encoding="utf-8") as f:
            #     f.write(first_train.get())
             
            # 处理直达列车的信息
            for item in self.process_direct_train(direct_trains):
                yield item
        
        # 获取所有包含中转信息的区域
        transfer_boxes = response.xpath('//div[@class="transfer-box"]')
        transfer_trains = transfer_boxes.xpath('.//div[@class="list-bd"]')
        self.logger.info(f"Found {len(transfer_trains) } transfer trains.")
        if transfer_trains:
            first_train = transfer_trains[0]
            # with open("FirstTransferTrain.txt", "w", encoding="utf-8") as f:
            #     f.write(first_train.get())
            for item in self.process_transfer_train(transfer_trains):
                yield item
    
        # 遍历景点信息
        # for train in direct_trains:
        #     # 创建 Item 对象并填充数据
        #     item = FindtripItem()
            

        #     item['DepartureTime'] = train.xpath('.//div[@class="from"]//div[@class="time"]/text()').get()
        #     #item['OriginCity'] = train.xpath('.//div[@class="from"]//div[@class="station"]/text()').get()
        #     item['Duration'] = train.xpath('.//div[@class="mid"]//div[@class="haoshi"]/text()').get()
        #     item['TrainNumber'] = train.xpath('.//div[@class="mid"]//div[@class="checi"]/text()').get()
        #     item['ArrivalTime'] = train.xpath('.//div[@class="to"]//div[@class="time"]/text()').get()
        #     #item['DestCity'] = train.xpath('.//div[@class="to"]//div[@class="station"]/text()').get()
        #     item['Price'] = train.xpath('.//div[@class="price"]/text()').get()
        #     item['Distance'] = "-"

        #     item['OriginCity'] = self.dStation
        #     item['DestCity'] = self.aStation

        #     yield item


    def errback_handle(self, failure):
        # 错误处理
        self.logger.error(f"Request failed: {failure.request.url}")

    def process_direct_train(self, trains):

        for train in trains:
            item = FindtripItem()

            item['DepartureTime'] = train.xpath('.//div[@class="from"]//div[@class="time"]/text()').get()
            #item['OriginCity'] = train.xpath('.//div[@class="from"]//div[@class="station"]/text()').get()
            item['Duration'] = train.xpath('.//div[@class="mid"]//div[@class="haoshi"]/text()').get()
            item['TrainNumber'] = train.xpath('.//div[@class="mid"]//div[@class="checi"]/text()').get()
            item['ArrivalTime'] = train.xpath('.//div[@class="to"]//div[@class="time"]/text()').get()
            #item['DestCity'] = train.xpath('.//div[@class="to"]//div[@class="station"]/text()').get()
            item['Price'] = train.xpath('.//div[@class="price"]/text()').get()
            item['Distance'] = "-"

            item['OriginCity'] = self.dStation
            item['DestCity'] = self.aStation

            item['TrainDate'] = self.travelDate

            yield item
    
    def process_transfer_train(self, trains):

        for train in trains:
            item = FindtripItem()

            item['DepartureTime'] = train.xpath('.//div[@class="from"]//div[@class="time"]/text()').get()
            #item['OriginCity'] = train.xpath('.//div[@class="from"]//div[@class="station"]/text()').get()
            item['Duration'] = train.xpath('.//div[@class="trans __web-inspector-hide-shortcut__"]/p[1]/text()').get()
            
            item['ArrivalTime'] = train.xpath('.//div[@class="to"]//div[@class="time"]/text()').get()
            #item['DestCity'] = train.xpath('.//div[@class="to"]//div[@class="station"]/text()').get()
            item['Price'] = train.xpath('.//div[@class="price"]/text()').get()
            item['Distance'] = "-"

            item['OriginCity'] = self.dStation
            item['DestCity'] = self.aStation
            item['TrainDate'] = self.travelDate

            TrainNumberText = train.xpath('.//ul[@class="surplus-list"]/li/text()').getall()
            #self.logger.info(f"Train Number Texts: {TrainNumberText}")
            TrainNumbers = []
            for text in TrainNumberText:
                if text and isinstance(text, str):  # 检查text是否为字符串且非空
                    match = re.search(r'[A-Z]\d+', text)
                    if match:
                        TrainNumbers.append(match.group())
            #TrainNumber = [re.search(r'[A-Z]\d+', text).group() for text in TrainNumberText]
            TrainNumberMerge = '/'.join(TrainNumbers) if TrainNumbers else "-"

            item['TrainNumber'] = TrainNumberMerge

            


            yield item