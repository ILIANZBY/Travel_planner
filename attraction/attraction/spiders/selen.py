import scrapy
import sys
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.http import HtmlResponse

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
    #name = 'Ctrip'
    
    now = datetime.now()
    six_days_later_str = (now + timedelta(days=6)).strftime('%Y-%m-%d')
    
    
    # cities = [
    #     "北京", "上海", "成都", "广州", "天津", "青岛", 
    #     "深圳", "合肥", "重庆", "济南", "西安", "杭州",
    #     "沈阳", "长沙", "南京", "沈阳", "厦门", "武汉",
    #     "郑州", 
    # ]

    cities = [
        "上海"
    ]

     # 城市名称到城市代号的映射字典
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
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 配置 Selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式（不显示浏览器窗口）
        chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 加速
        chrome_options.add_argument("--no-sandbox")  # 禁用沙盒模式
        chrome_options.add_argument("--disable-dev-shm-usage")  # 解决内存不足问题
        
        # 初始化 Chrome 浏览器
        self.driver = webdriver.Chrome(options=chrome_options)

    def closed(self, reason):
            # 关闭浏览器
            self.driver.quit()
    
    def start_requests(self):
        
        for city in self.cities:
            # 获取出发城市和到达城市的代号
            departure_code = self.city_code_mapping.get(city, "")
            # 去程: city -> Qinhuangdao
            outbound_url = f"https://flights.ctrip.com/online/list/oneway-{departure_code}-bpe?depdate={self.six_days_later_str}&cabin=y_s_c_f&adult=1&child=0&infant=0"
            yield scrapy.Request(outbound_url, callback=self.parse, meta={'departure_city': city, 'arrival_city': '秦皇岛'})
            
            # 返程: Qinhuangdao -> city
            return_url = f"https://flights.ctrip.com/online/list/oneway-bpe-{departure_code}?depdate={self.six_days_later_str}&cabin=y_s_c_f&adult=1&child=0&infant=0"
            yield scrapy.Request(return_url, callback=self.parse, meta={'departure_city': '秦皇岛', 'arrival_city': city})

    def parse(self, response):

         # 使用 Selenium 加载页面
        self.driver.get(response.url)
        
        # 等待页面加载完成（根据需要调整等待时间）
        self.driver.implicitly_wait(10)  # 隐式等待 10 秒
        
        # 获取渲染后的 HTML 内容
        html = self.driver.page_source
        
        # 将 HTML 内容传递给 Scrapy 的 Selector
        response = HtmlResponse(url=self.driver.current_url, body=html, encoding='utf-8')

        sel = scrapy.Selector(response)
        
        # 定位到包含每项飞机票信息的 div
        flights = sel.xpath("//div[@class='flight-item domestic']")
        
        # 将 flights 的 HTML 内容保存为 .txt 文件
        with open('flights_html.txt', 'w', encoding='utf-8') as f:
            sys.stdout = f  # 重定向标准输出到文件
            for flight in flights:
                print(flight.get())  # 打印每个 flight 的 HTML 内容
            sys.stdout = sys.__stdout__  # 恢复标准输出
        
        test = sel.xpath("//div[@id='hp_container']")
        with open('test_html.txt', 'w', encoding='utf-8') as f:
            sys.stdout = f  # 重定向标准输出到文件
            for flight in test:
                print(flight.get())  # 打印每个 flight 的 HTML 内容
            sys.stdout = sys.__stdout__  # 恢复标准输出

        items = []
        for flight in flights:
            item = FindtripItem()
            
            # 获取 flight-box 作为飞机票信息的具体内容区域
            flight_box = flight.xpath(".//div[@class='flight-box']")
            
            # 提取出发信息
            item['DepTime'] = flight_box.xpath(".//div[@class='depart-box']//div[@class='time']/text()").get()
            item['OriginCityName'] = response.meta['departure_city']  # 从 meta 中获取出发城市

            # 提取中间信息：行驶时间
            item['travel_duration'] = flight_box.xpath(".//div[@class='mid']//div[@class='haoshi']/text()").get()
            
            # 提取航班号
            flight_numbers = flight.xpath(".//div[@class='airline-name']/div/text()").getall()
            if flight_numbers:
                # 如果有多个航班号，用 / 连接
                item['Flight_Number'] = '/'.join(flight_numbers)
            else:
                item['Flight_Number'] = None
            
            # 提取到达信息
            item['ArrTime'] = flight_box.xpath(".//div[@class='arrive-box']//div[@class='time']/text()").get()
            item['DestCityName'] = response.meta['arrival_city']  # 从 meta 中获取到达城市
            
            # 提取价格信息
            item['Price'] = flight_box.xpath("//span[@class='price']/text()").getall()[-1].strip()

            # 将 item 添加到 items 列表
            items.append(item)
        
        return items

