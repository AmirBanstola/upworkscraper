from urllib.parse import urlencode

import scrapy
from scrapy.exceptions import CloseSpider




class UpworkSpider(scrapy.Spider):
    name = 'upwork_spider'
    allowed_domains = [
        'upwork.com'
    ]

    URL = 'https://www.upwork.com/freelance-jobs/{params}'
    MAX_PAGE = 500
    FREELANCERS_ON_PAGE = 10

    def __init__(self, search_key, query, page_limit=5, *args, **kwargs):
        super(UpworkSpider, self).__init__(*args, **kwargs)
        self.search_key = search_key
        self.query = query
        self.page_limit = min(int(page_limit), self.MAX_PAGE)

    def start_requests(self):
        for page in range(1, self.page_limit + 1):
            yield scrapy.Request(
                self.URL.format(params=urlencode({'q': self.query, 'page': page})),
                meta={'page': page}  # We'll use it later to calculate freelancer's rank
            )

    def parse(self, response):
        page = response.meta['page']
        for i, freelancer in enumerate(response.css('h4 a.job-tile-title')):
            name = freelancer.css('::text').extract_first().strip()
            profile_link = freelancer.css('::attr(href)').extract_first()
            rank = (page - 1) * self.FREELANCERS_ON_PAGE + i + 1
            yield {
                'title': name,
                'description': name,
                'profile_link': profile_link,
                'page': page,
                'rank': rank,
                'page_link': response.url,
                'data': freelancer.css('::attr(data-ng-click)').extract_first()
            }
            if self.profile_id in profile_link:
                raise CloseSpider(f'Your profile rank is {rank}. You are at page {page}: {response.url}')