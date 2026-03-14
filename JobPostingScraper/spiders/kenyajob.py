import scrapy
from JobPostingScraper.items import JobpostingscraperItem
from JobPostingScraper.itemloader import JobLoader
from datetime import datetime

class KenyajobSpider(scrapy.Spider):
    name = "kenyajob"
    allowed_domains = ["www.kenyajob.com"]
    start_urls = ["https://www.kenyajob.com/job-vacancies-search-kenya"]

    def __init__(self):
        self.next_page = 1

    def parse(self, response):
        # vertical repsonse
        job_links = response.xpath('//*[@id="main-content"]/div[2]/div/div[2]/div/div[2]/div[2]/div/div/h3/a/@href').getall()
        for link in job_links:
            yield response.follow(link,callback=self.parse_jobs)

        # horizonatal response
        page_links = response.xpath('//*[@id="main-content"]/div[2]/div/div[2]/div/div[3]/div/ul/li/a/@href').getall()
        next_url = f"/job-vacancies-search-kenya?page={self.next_page}"
        if next_url in page_links:
            self.next_page +=1
            yield response.follow(next_url,callback=self.parse)



    def parse_jobs(self,response):
        loader  = JobLoader(item=JobpostingscraperItem(),response=response)
        loader.add_value('url',response.url)
        loader.add_xpath("company",'//*[@id="main-content"]/div[2]/div[1]/div[1]/div[1]/div[2]/div/div/ul/li[1]/h3/a/text()')
        loader.add_value("posted_by","KenyaJob")
        loader.add_css("title","h1::text")
        loader.add_xpath('field','//*[@id="main-content"]/div[2]/div[1]/div[1]/div[1]/div[1]/div/ul/li[1]/span/div/div/div/text()')
        loader.add_value('date_posted',str(datetime.now()))
        loader.add_xpath('minimum_requirements','//*[@id="main-content"]/div[2]/div[1]/div[1]/div[2]/article/div/section[2]/div/ul/li/text()')
        loader.add_xpath('responsibilities','//*[@id="main-content"]/div[2]/div[1]/div[1]/div[2]/article/div/section[1]/div/ul/li/text()')
        loader.add_xpath('type','//*[@id="main-content"]/div[2]/div[1]/div[1]/div[1]/div[1]/div/ul/li[5]/span/text()')
        loader.add_xpath('location','//*[@id="main-content"]/div[2]/div[1]/div[1]/div[2]/article/div/section[3]/ul[1]/li[5]/span/text()')
        loader.add_value('application_method',"Follow URL of the advertiser to apply")
        loader.add_xpath('payment','//*[@id="main-content"]/div[2]/div[1]/div[1]/div[2]/article/div/section[3]/ul[1]/li[10]/span/text()')

        yield loader.load_item()
