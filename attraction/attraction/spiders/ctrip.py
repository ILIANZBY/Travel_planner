import scrapy

class FindtripItem(scrapy.Item):
    Name = scrapy.Field()                 # 景点名
    Latitude = scrapy.Field()             # 纬度
    Longitude = scrapy.Field()            # 经度
    Address = scrapy.Field()              # 地址
    Phone = scrapy.Field()                # 联系电话
    Website = scrapy.Field()              # 详情页链接  
    City = scrapy.Field()                 # 城市名

class AttractionSpider(scrapy.Spider):
    name = 'Ctrip'   #用命令行启动爬虫的名称
    allowed_domains = ['ctrip.com']

    results = []  # 定义一个列表来存储结果
    
    def start_requests(self):
        # 可以根据实际情况调整最大页数
        max_pages = 2
        for page in range(1, max_pages + 1):
            # 生成 URL，其中 {} 会被替换为当前的页码
            url = f"https://you.ctrip.com/sight/shanhaiguandistrict120556/s0-p{page}.html"
            self.logger.info(f"Start URL: {url}")
            yield scrapy.Request(url, callback=self.parse, errback=self.errback_handle)


    def parse(self, response):
        # 提取单个匹配的 div 节点
        card_list_box = response.xpath('//div[@class="cardListBox_box__lMuWz"]').get()
    
        if card_list_box:
            # 打印到命令行
            print("Card List Box HTML:")
            print(card_list_box)
        # 保存页面 HTML 以供调试
        # with open("response.html", "w", encoding="utf-8") as f:
        #     f.write(response.text)

        # 定位到景点信息区域
        attractions = response.xpath('//div[@class="sightItemCard_box__2FUEj "]')
        self.logger.info(f"Found {len(attractions)} attractions.")

        # 遍历景点信息
        for attraction in attractions:
            # 提取景点名称和链接
            name = attraction.xpath('.//div[@class="titleModule_name__Li4Tv"]/span/a/text()').get()
            link = attraction.xpath('.//div[@class="titleModule_name__Li4Tv"]/span/a/@href').get()

            # 如果链接是完整的 URL，直接使用
            if link:
                yield scrapy.Request(
                    url=link,
                    callback=self.parse_detail,  
                    meta={'Name': name, 'Link': link}
                )

    def parse_detail(self, response):
        # 创建一个存储景点信息的 item
        item = FindtripItem()

        # 从详情页和主页面提取数据，存入字典
        item = {
            "Name": response.meta['Name'],  # 从主页面传递的景点名称
            "Website": response.meta['Link'],  # 从主页面传递的详情页链接

             # 从详情页提取信息
            "Address": response.xpath(
                '//div[@class="baseInfoItem"]/p[@class="baseInfoTitle" and text()="地址"]/following-sibling::p[@class="baseInfoText"]/text()'
            ).get(),

            "Phone": response.xpath(
                '//div[@class="baseInfoItem"]/p[@class="baseInfoTitle" and text()="官方电话"]/following-sibling::p[@class="baseInfoText"]/text()'
            ).get(),

           "Latitude": response.xpath('//meta[@name="latitude"]/@content').get(),
           "Longitude": response.xpath('//meta[@name="longitude"]/@content').get(),

           # 手动设置城市信息
           "City": "QingHuangDao"
        }

        # 打印提取的信息到日志中，便于调试
        self.logger.info(f"Scraped Detail: {item}")

        # 将数据返回给 Scrapy 的 pipeline 或保存
        yield item



    def errback_handle(self, failure):
        # 错误处理
        self.logger.error(f"Request failed: {failure.request.url}")
