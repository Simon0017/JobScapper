import scrapy
from JobPostingScraper.items import JobpostingscraperItem
from JobPostingScraper.itemloader import JobLoader

class CorporatestaffingSpider(scrapy.Spider):
    name = "CorporateStaffing"
    allowed_domains = ["www.corporatestaffing.co.ke"]
    start_urls = ["https://www.corporatestaffing.co.ke/jobs/"]

    def parse(self, response):
        # vertical crawling
        job_links = response.xpath('//*[@id="archive-container"]/li/article/div/header/h2/a/@href').getall()
        for job in job_links:
            yield response.follow(job,callback = self.parse_job)

        # horizantal craling 
        pages_links = response.xpath('//*[@id="main"]/nav/div/a/@href').getall()
        try:
            current_page = int(response.url.split('/')[-1])
            next_page = int(pages_links[-1].split('/')[-1])
            if next_page > current_page: # only follow if there is a valid next page
                yield response.follow(pages_links[-1],callback = self.parse)
        except:
             yield response.follow(pages_links[-1],callback = self.parse)
        
    def parse_job(self,response):
        loader  = JobLoader(item=JobpostingscraperItem(),response=response)
        loader.add_value('url',response.url)
        loader.add_value("posted_by","Corporate Staffing Services")
        loader.add_xpath("title",'//*[@id="post-274585"]/div/header/h1/text()')
        loader.add_xpath('field','//*[@id="main"]/div[1]/span/span[3]/a/text()')
        loader.add_xpath('minimum_requirements','/html/body/div[1]/main/div/div/div/div[2]/article/div/div/ul/li/text()')
        yield loader.load_item()