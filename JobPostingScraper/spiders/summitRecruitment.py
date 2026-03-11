import scrapy
from JobPostingScraper.items import JobpostingscraperItem
from JobPostingScraper.itemloader import JobLoader

class SummitrecruitmentSpider(scrapy.Spider):
    name = "summitRecruitment"
    allowed_domains = ["summitrecruitment-search.com"]
    start_urls = ["https://summitrecruitment-search.com/job-board/"]

    def parse(self, response):
        links = response.css('a.button.background002e3e::attr(href)').getall() 
        for link in links:
            yield response.follow(link,callback=self.parse_job)

    def parse_job(self,response):
        loader  = JobLoader(item=JobpostingscraperItem(),response=response)
        loader.add_value('url',response.url)
        loader.add_value("posted_by","Summer Recruitment")
        loader.add_xpath("title",'//header/h1/text()')
        loader.add_xpath('minimum_requirements','//div/ul[2]/li/text()')
        loader.add_xpath('responsibilities','//div/ul[1]/li/text()')
        loader.add_xpath('type','//footer/div/p/text()[8]')
        loader.add_xpath('location','//footer/div/p/text()[4]')
        loader.add_xpath('application_method','//div/section[2]/a/@href')
        loader.add_xpath('payment','//footer/div/p/text()[2]')
        loader.add_xpath("application_deadline",'//footer/div/p/text()[10]')

        yield loader.load_item()
