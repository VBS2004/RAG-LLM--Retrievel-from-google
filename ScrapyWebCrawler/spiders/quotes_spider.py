import scrapy
from scrapy_splash import SplashRequest
from urllib.parse import urlparse, parse_qs

class QuotesSpider(scrapy.Spider):
    name = 'quotes'

    def start_requests(self):
        url = 'https://www.google.com/search?q=aws+saa+voucher'
        yield SplashRequest(url, callback=self.parse, args={'wait': 2})

    def parse(self, response):
        # Using CSS selectors to find anchor tags containing h3 elements
        for link in response.css('a:has(h3)'):
            # Extracting the necessary data
            href = link.attrib.get('href')
            parsed = urlparse(href)
            actual_link = parse_qs(parsed.query).get('q', [None])[0]
            if actual_link:
                yield {
                    'link': actual_link
                }
