import re

from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from scrapy.selector import Selector
from scrapy.item import Item
from scrapy.linkextractors import LinkExtractor

from corporatebonds.items import BondItem

class SecSpider(CrawlSpider):
    name = "sec"
    allowed_domains = ["sec.gov"]
    initial_item_count = 100
    url_template = None
    
    def __init__(self, symbol=None, *args, **kwargs):
        super(SecSpider, self).__init__(*args, **kwargs)
        self.url_template = 'https://www.sec.gov/cgi-bin/browse-edgar?CIK=%s&type=424B2&dateb=&owner=exclude&count=100' % symbol
        self.start_urls = [self.url_template]
        self.initial_item_count = 100
        self.current_item_count = 0
        
    def parse(self, response):
        self.parse_sec_page(response)
        #https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000029915&type=&dateb=&owner=exclude&start=1300&count=100
        page = response.xpath("//div[@id='contentDiv']/div/form/table/tr/td/input[@value='Next 100']").extract_first()
        if page:
            self.current_item_count += self.initial_item_count
            url = self.url_template + "&start=%s" % self.current_item_count
            yield Request(response.urljoin(url), callback=self.parse)
    
    def parse_sec_page(self, response):
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
                yield Request(response.urljoin(url), callback=self.parse_sec_page)
          
        for url in response.xpath("//table[@summary='Results']/tr/td[2]/a/@href").extract():
            yield Request(response.urljoin(url), callback=self.parse_sec_page)
            