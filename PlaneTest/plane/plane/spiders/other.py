import scrapy
import sys
import time
import random
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class FindtripItem(scrapy.Item):
    Flight_Number = scrapy.Field()                 # 航班号
    Price = scrapy.Field()                         # 价格 
    DepTime = scrapy.Field()                       # 出发时间
    ArrTime = scrapy.Field()                       # 到达时间
    ActualElapsedTime = scrapy.Field()             # 飞行时间
    FlightDate = scrapy.Field()                    # 航班日期  
    OriginCityName = scrapy.Field()                # 出发城市名
    DestCityName = scrapy.Field()                  # 到达城市名
    Distance = scrapy.Field()                      # 距离

class CtripSpider(scrapy.Spider):
    #name = 'ctrip'
    
    
    cities = [
        "上海"
    ]

    city_code_mapping = {
        "北京": "bjs",  # 北京
        "上海": "sha",  # 上海
        "成都": "ctu",  # 成都
        "广州": "can",  # 广州
        "天津": "tsn",  # 天津
        "青岛": "tao",  # 青岛
        "深圳": "szx",  # 深圳
        "合肥": "hfe",  # 合肥
        "重庆": "ckg",  # 重庆
        "济南": "tna",  # 济南
        "西安": "sia",  # 西安
        "杭州": "hgh",  # 杭州
        "沈阳": "she",  # 沈阳
        "长沙": "csx",  # 长沙
        "南京": "nkg",  # 南京
        "厦门": "xmn",  # 厦门
        "武汉": "wuh",  # 武汉
        "郑州": "cgo",  # 郑州
        "秦皇岛": "bpe",# 秦皇岛
    }

    def __init__(self, dStation=None, aStation=None, *args, **kwargs):
        super(CtripSpider, self).__init__(*args, **kwargs)
        if not dStation and not aStation:
            raise ValueError("Both Departure Station(dStation) and Arrival Station(aStation) must be provided.")
        self.dStation = dStation
        self.aStation = aStation
        now = datetime.now()
        self.six_days_later_str = (now + timedelta(days=6)).strftime('%Y-%m-%d')

        # 初始化Selenium WebDriver
        self.driver = self.init_driver()

    def init_driver(self):
        options = webdriver.ChromeOptions()
        
        # 定义一组常用的 User-Agent 字符串
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1"
        ]
        
        # 随机选择一个 User-Agent
        options.add_argument(f"user-agent={random.choice(user_agents)}")
        
        # 其他选项可以根据需要添加
        # options.add_argument("--headless")  # 无头模式
        # options.add_argument("--disable-gpu")
        # options.add_argument("--no-sandbox")
        
        return webdriver.Chrome(options=options)

    def closed(self, reason):
        # 关闭WebDriver
        self.driver.quit()

    def start_requests(self):
        
        departure_code = self.city_code_mapping.get(self.dStation,"")
        arrival_code = self.city_code_mapping.get(self.aStation,"")
        url = f"https://flights.ctrip.com/online/list/oneway-{departure_code}-{arrival_code}?depdate={self.six_days_later_str}&cabin=y_s_c_f&adult=1&child=0&infant=0"

        self.logger.info(f"Generated URL: {url}")
        yield scrapy.Request(url=url, callback=self.parse, meta={'departure_city': self.dStation, 'arrival_city': self.aStation})

    def parse(self, response):
        # 使用Selenium加载页面
        self.driver.get(response.url)

        # 设置一个随机延迟，范围在1到2秒之间
        delay = random.uniform(1, 2)
        time.sleep(delay)
        
        # 等待页面加载完成
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "flight-list"))
        )
        
        # 获取页面源码
        page_source = self.driver.page_source
        
        # 将HTML内容保存为.txt文件
        with open('html.txt', 'w', encoding='utf-8') as f:
            f.write(page_source)
        
        sel = scrapy.Selector(text=page_source)
        
        # 定位到包含每项飞机票信息的 div
        flights = sel.xpath("//div[@class='flight-item domestic']")
        
        # 将flights的HTML内容保存为.txt文件
        with open('flights_html.txt', 'w', encoding='utf-8') as f:
            for flight in flights:
                f.write(flight.get() + "\n")
        
        # test = sel.xpath("//div[@id='hp_container']")
        # with open('test_html.txt', 'w', encoding='utf-8') as f:
        #     for flight in test:
        #         f.write(flight.get() + "\n")

        flightNum = sel.xpath(".//span[@class='plane-No']")
        with open('flights_num_html.txt', 'w', encoding='utf-8') as f:
            for flight in flightNum:
                f.write(flight.get() + "\n")

        items = []
        for flight in flights:
            item = FindtripItem()
            
            flight_box = flight.xpath(".//div[@class='flight-box']")
            
            item['DepTime'] = flight_box.xpath(".//div[@class='depart-box']//div[@class='time']/text()").get()
            item['OriginCityName'] = response.meta['departure_city']
            
            #item['ActualElapsedTime'] = flight_box.xpath(".//div[@class='mid']//div[@class='haoshi']/text()").get()
            

            flight_numbers = flight.xpath(".//span[@class='plane-No']/text()").getall()
            if flight_numbers:
                item['Flight_Number'] = '/'.join(flight_numbers)
            else:
                item['Flight_Number'] = None
            
            item['ArrTime'] = flight_box.xpath(".//div[@class='arrive-box']//div[@class='time']/text()").get()
            item['DestCityName'] = response.meta['arrival_city']
            
            item['Price'] = flight_box.xpath(".//span[@class='price']/text()").getall()[-1].strip()

            items.append(item)
        
        return items

