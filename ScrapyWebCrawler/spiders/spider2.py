import scrapy
from scrapy_splash import SplashRequest
from urllib.parse import urlparse, parse_qs
from readability import Document
import requests
import regex as re
from bs4 import BeautifulSoup


count=0
class QuotesSpider(scrapy.Spider):
    name = 'quotes2'

    def start_requests(self):
        url = 'https://www.google.com/search?q=who+is+the+current+prime+minister+of+India'
        yield SplashRequest(url, callback=self.parse, args={'wait': 2})

    def parse(self, response):
        global count
        for link in response.css('a:has(h3)'):
            if(count>10):
                break;
            href = link.attrib.get('href')
            parsed = urlparse(href)
            actual_link = parse_qs(parsed.query).get('q', [None])[0]
            if actual_link:
                if "youtube" not in actual_link:
                    count+=1
                    yield SplashRequest(actual_link,callback=self.othersiteparse,args={'wait':6})
        if(count<10):
            try:
                yield SplashRequest(response.css("#pnnext").attrib.get('href'),callback=self.parse,args={'wait':6})
            except:
                pass
    def othersiteparse(self,response):
        content_methods = [
            self.extract_by_common_tags,
            self.extract_by_class,
            #self.extract_by_xpath,
            self.extract_by_regex
        ]

        results = set()
        for method in content_methods:
            results.update(method(response))
        result=" ".join(results)
        soup=BeautifulSoup(result)
        result=soup.get_text()
        yield {
            'url': response.url,
            'title': response.css('title::text').get(),
            'extraction_results': result
        }
    def extract_by_common_tags(self, response):
        content_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'span', 'div']
        content = []
        for tag in content_tags:
            content.extend(response.css(f'{tag}::text').getall())
        return self.clean_content(content)

    def extract_by_class(self, response):
        # Experiment with different class names that might contain main content
        content_classes = ['.main-content', '.article-body', '.post-content']
        content = []
        for cls in content_classes:
            content.extend(response.css(f'{cls} ::text').getall())
        return self.clean_content(content)

    def extract_by_xpath(self, response):
        # Experiment with XPath to target specific structures
        xpaths = [
            '//div[@id="content"]//text()',
            '//article//text()',
            '//main//text()'
        ]
        content = []
        for xpath in xpaths:
            content.extend(response.xpath(xpath).getall())
        return self.clean_content(content)

    def extract_by_regex(self, response):
        # Experiment with regex patterns to extract content
        patterns = [
            r'<p>(.*?)</p>',
            r'<article>(.*?)</article>'
        ]
        content = []
        for pattern in patterns:
            content.extend(re.findall(pattern, response.text, re.DOTALL))
        return self.clean_content(content)
    def removegraphic(self,i):
        res=""
        for char in i:
            if(ord(char)>=32 and ord(char)<=126):
                res+=char
        return res

    def clean_content(self, content):
        # Clean and process the extracted content
        cleaned = [text.strip() for text in content if text.strip()]
        for i in cleaned:
            if "cookies" in i:
                cleaned.remove(i)
        # Remove very short snippets
        cleaned = [text.replace("\n"," ") for text in cleaned if len(text) > 5]
        cleaned=list(map(self.removegraphic,cleaned))
        # Join the cleaned text, limiting to first 1000 characters for brevity
        return cleaned