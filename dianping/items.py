# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DianpingRestaurant(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    address = scrapy.Field()
    longitude = scrapy.Field()
    latitude = scrapy.Field()
    phone = scrapy.Field()
    average_consumpiton = scrapy.Field()
    business_hours = scrapy.Field()
    cuisine = scrapy.Field()
    sub_suisine = scrapy.Field()
    region = scrapy.Field()
    sub_region = scrapy.Field()
    last_update_time = scrapy.Field()
