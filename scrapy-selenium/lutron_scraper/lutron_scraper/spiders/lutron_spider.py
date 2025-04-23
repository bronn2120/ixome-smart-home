import scrapy

class LutronSpider(scrapy.Spider):
    name = 'lutron'
    start_urls = [
        'https://support.lutron.com/us/en',
        'https://support.lutron.com/us/en/product/maestro/article/troubleshooting/The-Maestro-Dimmer-is-Blinking'
    ]
    custom_settings = {
        'CLOSESPIDER_PAGECOUNT': 100,
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.RFPDupeFilter',
        'DOWNLOAD_DELAY': 3,
    }
    seen_texts = set()

    def parse(self, response):
        texts = response.css('div.article-body ::text').getall()
        for text in texts:
            cleaned_text = text.strip()
            if cleaned_text and len(cleaned_text) > 50 and cleaned_text not in self.seen_texts:
                self.seen_texts.add(cleaned_text)
                yield {'text': cleaned_text}

        for next_page in response.css('div.top-category-list-content a::attr(href), a.use-ajax-custom::attr(href), a[href*="/article/"]::attr(href)').getall():
            if 'support' or 'help' in next_page.lower():
                if next_page.startswith(('http://', 'https://')):
                    yield response.follow(next_page, self.parse)
