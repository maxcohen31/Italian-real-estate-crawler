import scrapy
from scrapy.crawler import CrawlerProcess


class ImmoSpider(scrapy.Spider):
    name = 'immobiliare_real_estate'
    
    start_urls = [
        'https://www.immobiliare.it/en/vendita-case/milano-provincia/?criterio=rilevanza'
    ]
    allowed_domains = ['immobiliare.it']
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
    }


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url, 
                headers=self.headers, 
                callback=self.parse_links
            )
            break

    def parse_links(self, response):
        all_links = response.xpath("//a[@class='in-breadcrumb__dropdownLink']/@href").getall()

        for link in all_links:
            with open('links.txt', 'a+') as f:
                f = f.write(f"{str(link)}?criterio=rilevanza\n")
        
# main driver
if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(ImmoSpider)
    process.start()
    
    