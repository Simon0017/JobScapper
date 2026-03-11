import scrapy
from JobPostingScraper.items import JobpostingscraperItem
from JobPostingScraper.itemloader import JobLoader

class MyjobmagSpider(scrapy.Spider):
    name = "MyJobMag"
    allowed_domains = ["www.myjobmag.co.ke"]
    start_urls = ["https://www.myjobmag.co.ke/jobs-by-field"]

    def parse(self, response):
        field_links = response.xpath('//*[@id="jobs-sec"]/div/div/div/ul//li//a/@href').getall()

        for link in field_links:
            yield response.follow(link,callback = self.parse_field_info)
    
    def parse_field_info(self,response):
        # vertical
        job_links = response.xpath('//*[@id="cat-left-sec"]/ul/li/ul/li/ul/li/h2/a/@href').getall()
        for job in job_links:
            yield response.follow(job,callback = self.parse_job_data)
        
        # horizontal
        next_pages = response.xpath('//*[@id="cat-left-sec"]/div[3]/ul/li/a/@href').getall()
        for page in next_pages:
            yield response.follow(page,callback = self.parse_field_info)
    
    def parse_job_data(self,response):
        loader  = JobLoader(item=JobpostingscraperItem(),response=response)
        loader.add_value('url',response.url)
        loader.add_value("posted_by","MyJobMag")
        loader.add_css("title","h1::text")
        loader.add_xpath('field','//*[@id="printable"]/ul/li[5]/span[2]/a/text()')
        loader.add_xpath('date_posted','//*[@id="posted-date"]/text()')
        loader.add_xpath("application_deadline",'//*[@id="read-content-wrap"]/div/div[1]/ul/li[1]/div/div[2]/text()')
        loader.add_xpath('minimum_requirements','//*[@id="printable"]/div[2]/ul[6]/li/text()')
        loader.add_xpath('minimum_requirements','//*[@id="printable"]/div[2]/ul[7]/li/text()')
        loader.add_xpath('responsibilities','//*[@id="printable"]/div[2]/ul/li/text()')
        loader.add_xpath('type','//*[@id="printable"]/ul/li[1]/span[2]/a/text()')
        loader.add_xpath('location','//*[@id="printable"]/ul/li[4]/span[2]/a/text()')
        loader.add_xpath('application_method','//*[@id="printable"]/div[4]/p[1]//text()')

        yield loader.load_item()