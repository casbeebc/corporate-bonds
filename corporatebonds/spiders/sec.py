import re

from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from scrapy.selector import Selector
from scrapy.item import Item

from corporatebonds.items import BondItem

class SecSpider(CrawlSpider):
    name = "sec"
    allowed_domains = ["sec.gov"]
    
    def __init__(self, symbol=None, *args, **kwargs):
        super(SecSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['https://www.sec.gov/cgi-bin/browse-edgar?CIK=%s&type=424B2&dateb=&owner=exclude&count=100' % symbol]
    
    def parse(self, response):
        foundProspectus = False
        
        for searchText in response.xpath("//*[contains(text(),'Ratio of Earnings')]"):
            foundProspectus = True
            break
            
        if foundProspectus:
            item = scrapy.Item()
            item['url'] = response.url
            return item
            
            
        for url in response.xpath("//table[@summary='Document Format Files']/tr/td/a/@href").extract():
            if re.compile(r".*\.htm").match(url) is not None:
                yield Request(response.urljoin(url), callback=self.parse)
          
        for url in response.xpath("//table[@summary='Results']/tr/td[2]/a/@href").extract():
            yield Request(response.urljoin(url), callback=self.parse)