import scrapy
from JobPostingScraper.items import JobpostingscraperItem
from JobPostingScraper.itemloader import JobLoader

class BrightermondaySpider(scrapy.Spider):
    name = "brighterMonday"
    allowed_domains = ["www.brightermonday.co.ke"]
    start_urls = ["https://www.brightermonday.co.ke/jobs"]

    def __init__(self):
        self.page_counter = 1

    def parse(self, response):
        # vertical crawling
        links =  response.xpath('/html/body/main/section/div[3]/div[2]/div[1]/div/div/div/div/div/a/@href').getall()
        for link in links:
            yield response.follow(link,callback=self.parse_job)

        # horixontal crawling
        base_url = "https://www.brightermonday.co.ke/jobs"
        try:
            self.page_counter += 1
            next_url = f"{base_url}?page={self.page_counter}"
            print(f"Crawling to url: {next_url}")
            yield response.follow(next_url,callback = self.parse)
        except:
            return


    def parse_job(self,response):
        loader  = JobLoader(item=JobpostingscraperItem(),response=response)
        loader.add_value('url',response.url)
        loader.add_value("posted_by","BrighterMonday")
        loader.add_css("title",'h1.font-bold::text')
        loader.add_xpath('field','/html/body/main/section/div[2]/div/div[2]/div[1]/div/div/article/div[1]/div[1]/div[2]/h2[2]/a/text()')
        loader.add_xpath('date_posted','/html/body/main/section/div[2]/div/div[2]/div[1]/div/div/article/div[1]/div[1]/div[2]/span/text()')
        loader.add_xpath('minimum_requirements','/html/body/main/section/div[2]/div/div[2]/div[1]/div/div/article/div[1]/div[3]/div/span[1]/span/text()')
        loader.add_xpath('responsibilities','/html/body/main/section/div[2]/div/div[2]/div[1]/div/div/article/div[1]/div[4]/div/div/text()')
        loader.add_xpath('type','/html/body/main/section/div[2]/div/div[2]/div[1]/div/div/article/div[1]/div[1]/div[5]/a[2]/text()')
        loader.add_xpath('location','/html/body/main/section/div[2]/div/div[2]/div[1]/div/div/article/div[1]/div[1]/div[5]/a[1]/text()')
        loader.add_value('application_method',"MUST LOGIN TO BRIGHTER MONDAY TO APPLY")
        loader.add_xpath('payment','/html/body/main/section/div[2]/div/div[2]/div[1]/div/div/article/div[1]/div[1]/div[5]/span/text()')

        yield loader.load_item()
