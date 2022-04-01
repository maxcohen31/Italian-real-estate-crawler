import json
import scrapy
from scrapy.crawler import CrawlerProcess


class ImmoScraper(scrapy.Spider):
    
    name = 'real_estate_scraper'
    
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
    }
    
    custom_settings = {
        
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'AUTOTHROTTLE_ENABLED': True
    }
    
    # spider's entry point
    def start_requests(self):
        
        with open('links.txt') as f:
            links = f.read().split('\n')
        
        # loop over list of initial links to crawl
        for link in links:
            # initial HTTP request
            yield scrapy.Request(
                url=link,
                headers=self.headers,
                callback=self.parse_pages
            )   
        
    def parse_pages(self, response):
        
        # total pages
        try:
            tot_pages = int(response.xpath("//div[@class='in-pagination__list']//text()").getall()[-1])
        except:
            tot_pages = 1
        
        # loop over pages and calls the self.parse_links method  
        for page in range(2, tot_pages):
            next_page = response.url + '&pag=' + str(page) 
            
            yield response.follow(
                url=next_page,
                headers=self.headers,
                callback=self.parse_links
            )
            
        
    def parse_links(self, response):
        
        # list of links
        cards = [
            link for link in response.xpath("//a[@class='in-card__title']/@href").getall()
            ]
        
        # loop over the links every card embeds
        for card_url in cards:
            yield response.follow(
                url=card_url,
                headers=self.headers,
                callback=self.parse_listings
            )
            
    # extracting the selected data
    def parse_listings(self, response):
        
        features = {
                            
            'Name': response.xpath("//span[@class='im-titleBlock__title']//text()").get(),  
            'Rooms': response.xpath("//span[@class='im-mainFeatures__value']//text()").get().strip(),
            'Description': response.xpath("//div[@class='im-description__text js-readAllText js-description-text']//text()").get().strip(),
            'Price': response.xpath("//div[@class='im-mainFeatures__title']//text()").get().strip().replace('\u20ac ', ''),
            'Energy Efficiency': response.xpath("//span[@class='im-features__energy']/following-sibling::text()").get().strip().replace('/m\u00b2 ', '/m^2 per '),
            'Agency': response.xpath("//div[@class='im-lead__reference']//a/@href").get()
        }    
        
        # write data on a jsonl file
        with open('properties.jsonl', 'a') as f:
            f.write(json.dumps(features) + '\n')
        
# main driver
if __name__ == '__main__':

    # run scraper
    process = CrawlerProcess()
    process.crawl(ImmoScraper)
    process.start()
            
