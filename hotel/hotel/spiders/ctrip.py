import scrapy

class FindtripItem(scrapy.Item):
    HotelName = scrapy.Field()                 # 景点名
    RoomType = scrapy.Field()             # 纬度
    Price = scrapy.Field()            # 经度
    Minimum = scrapy.Field()              # 地址
    ReviewRate = scrapy.Field()
    HouseRules = scrapy.Field()                # 联系电话
    MaximumOccupancy = scrapy.Field()              # 详情页链接  
    City = scrapy.Field()                 # 城市名


class HotelSpider(scrapy.Spider):
    name = 'Ctrip'   #用命令行启动爬虫的名称
    allowed_domains = ['hk.trip.com']
    
    results = []

    def start_requests(self):
       
        url = f"https://hk.trip.com/hotels/list?city=147&optionId=295&optionType=Location&display=%E5%B1%B1%E6%B5%B7%E5%85%B3%E5%8C%BA&tid=H0008_10650006152_entry&locale=zh-HK&curr=HKD"
        self.logger.info(f"Start URL: {url}")
        yield scrapy.Request(url, callback=self.parse, errback=self.errback_handle)


    def parse(self, response):
        
    
        # 保存页面 HTML 以供调试
        # with open("response.html", "w", encoding="utf-8") as f:
        #     f.write(response.text)

        # 定位到景点信息区域
        hotels = response.xpath('//div[@class="hotel-info"]')
        self.logger.info(f"Found {len(hotels)} hotels.")
        # if hotels:
        #     first_hotel = hotels[0]
        #     with open("FirstHotel.txt", "w", encoding="utf-8") as f:
        #         f.write(first_hotel.get())
    
        # 遍历景点信息
        for hotel in hotels:
            # 创建 Item 对象并填充数据
            item = FindtripItem()
            

            # 提取景点名称和链接
            HotelName = hotel.xpath('.//span[@class="name"]/text()').get()
            ReviewRate = hotel.xpath('.//span[@class="real"]/text()').get().strip()

            Price = response.xpath('//div[@id="meta-real-price"]//div/text()').get().strip()

            item['HotelName'] = HotelName
            item['ReviewRate'] = ReviewRate
            item['Price'] = Price
            item['Minimum'] = "1"
            item['RoomType'] = "双床房"
            item['HouseRules'] = "No Smoking"
            item['MaximumOccupancy'] = '2'
            item['City'] = "秦皇岛"

            yield item


    def errback_handle(self, failure):
        # 错误处理
        self.logger.error(f"Request failed: {failure.request.url}")
