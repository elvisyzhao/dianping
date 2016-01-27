#coding=utf-8

import scrapy
import logging
from dianping.items import DianpingRestaurant
from redis import Redis

logger = logging.getLogger()

class RestaurantSpider(scrapy.spiders.Spider):
    name = "restaurant"
    allowed_domains = ["dianping.com"]
    start_urls = ["http://www.dianping.com/beijing/food"]

    def parse(self, response):
        cuisines = response.selector.xpath("//*[@class='J_auto-load']/*[1]/div/ul[@class='cooking_term']/li/a")
        for cuisine in cuisines:
            name = cuisine.xpath(".//strong/text()").extract()[0]
            identifier = cuisine.xpath(".//@data-value").extract()[0]
            url = "http://www.dianping.com/search/category/2/10/g" + identifier
            yield scrapy.Request(url, callback=self.parse_sub_cuisine, meta={"cuisine" : name})

    # 解析子分类
    def parse_sub_cuisine(self, response):
        sub_cuisines = response.selector.xpath("//div[@id='classfy-sub']/a")
        for sub_cuisine in sub_cuisines:
            name = sub_cuisine.xpath("span/text()").extract()[0]
            if name == u"不限":
                continue
            else:
                url_suffix = sub_cuisine.xpath("@href").extract()[0]
                url = "http://www.dianping.com" + url_suffix
                dic = response.meta
                dic["sub_cuisine"] = name
                yield scrapy.Request(url, callback=self.parse_region, meta=dic)

        if len(sub_cuisines) == 0:
            self.parse_region(response)

    # 解析区域
    def parse_region(self, response):
        regions = response.selector.xpath("//div[@id='region-nav']/a")

        for region in regions:
            region_name = region.xpath("span/text()").extract()[0]
            url_suffix = region.xpath("@href").re(r"g\d+([a-z]\d+)")[0]
            url = response.url + url_suffix 
            dic = response.meta
            dic["region"] = region_name
            yield scrapy.Request(url, callback=self.parse_sub_region, meta=dic)

    # 解析子区域
    def parse_sub_region(self, response):
        sub_regions = response.selector.xpath("//div[@id='region-nav-sub']/a")
        dic = response.meta
        cuisine = dic.get("cuisine")
        sub_cuisine = dic.get("sub_cuisine", "none")
        region = dic.get("region")
        for sub_region in sub_regions:
            name = sub_region.xpath("span/text()").extract()[0]
            if name == u"不限":
                continue
            else:
                url_suffix = sub_region.xpath("@href").extract()[0]
                url = "http://www.dianping.com" + url_suffix
                dic["sub_region"] = name
                logger.info("cuisine : %s sub_cuisine : %s region : %s sub_region : %s", cuisine, sub_cuisine, region, name)
                yield scrapy.Request(url, callback=self.parse_first_page, meta=dic)

        if len(sub_regions) == 0:
            logger.info("cuisine : %s sub_cuisine : %s region : %s sub_region : %s", cuisine, sub_cuisine, region, "none")
            self.parse_first_page(response)
            
    # 解析列表
    def parse_first_page(self, response):
        pages = response.selector.xpath("//body[@id='top']/div[6][@class='section Fix']/div[3][@class='content-wrap']/div[1][@class='shop-wrap']/div[2][@class='page']/a[@class='PageLink']/@title").extract()
        if len(pages) > 0:
            pagesCount = int(pages[-1])
            for i in range(2, pagesCount+1):
                url = "%sp%d" % (response.url, i)
                yield scrapy.Request(url, callback=self.parse_other_page)

        shop_url_list = response.selector.xpath("//div[@class='tit']/a[1]/@href").extract()
        for shop_url in shop_url_list:
            url = "http://www.dianping.com" + shop_url
            logger.info(url)
            yield scrapy.Request(url, callback=self.parse_restaurant)

    def parse_other_page(self, response):
        shop_url_list = response.selector.xpath("//div[@class='tit']/a[1]/@href").extract()
        for shop_url in shop_url_list:
            url = "http://www.dianping.com" + shop_url
            logger.info(url)
            yield scrapy.Request(url, callback=self.parse_restaurant)

    # 解析门店
    def parse_restaurant(self, response):
        coordinate = response.selector.xpath("//*[@id='aside']/script[1]/text()").re(r"{lng:(\d+.\d+),lat:(\d+\.\d+)}")
        name = response.selector.xpath("//div[@id='basic-info' and @class='basic-info default nug_shop_ab_pv-a']/h1[@class='shop-name']/text()").extract()[0]
        name = name.strip()
        if (len(coordinate) == 2):
            lng = coordinate[0]
            lat = coordinate[1]
            logger.info("restaurant's name is %s, coordinate is %s, %s", name, lng, lat)
        else:
            pass
