import scrapy
from JobPostingScraper.items import JobpostingscraperItem
from JobPostingScraper.itemloader import JobLoader

class ReliefwebSpider(scrapy.Spider):
    name = "reliefweb"
    allowed_domains = ["reliefweb.int"]
    start_urls = ["https://reliefweb.int/jobs?list=Kenya"]

    def __init__(self):
        self.current_page = 0

    def parse(self, response):
        # vertical crawling
        job_links = response.xpath("//div[2]/article/header/h3/a/@href").getall()
        for link in job_links:
            yield response.follow(link,callback=self.parse_jobs)

        # horizontal crawling
        page_links = response.xpath("//*[@id='main-content']/div/div/div/section/nav/ul/li/a/@href").getall()
        page_no = [link.split("=")[-1] for link in page_links]
        page_no_ints = list(map(lambda x:int(x),page_no))
        self.current_page += 1
        if self.current_page in page_no_ints:
            url  = f"https://reliefweb.int/jobs?list=Kenya&page={self.current_page}"
            yield response.follow(url,callback=self.parse)
    

    def parse_jobs(self,response):
        loader  = JobLoader(item=JobpostingscraperItem(),response=response)
        loader.add_value('url',response.url)
        loader.add_xpath("company",'//*[@id="main-content"]/div/div/div/article/header/dl/dd[1]/ul/li/a/text()')
        loader.add_value("posted_by","ReliefWeb")
        loader.add_css("title","h1::text")
        loader.add_xpath('field','//*[@id="details"]/dl/dd[4]/ul/li/a/text()')
        loader.add_xpath('date_posted','//*[@id="main-content"]/div/div/div/article/header/dl/dd[2]/time/@datetime')
        loader.add_xpath("application_deadline",'//*[@id="main-content"]/div/div/div/article/header/dl/dd[3]/time/@datetime')
        loader.add_xpath('minimum_requirements','//*[@id="main-content"]/div/div/div/article/div/ul[1]/li/text()')
        loader.add_xpath('responsibilities','//*[@id="main-content"]/div/div/div/article/div/ol/li/ul/li/text()')
        loader.add_xpath('type','//*[@id="details"]/dl/dd[3]/ul/li/a/text()')
        loader.add_xpath('location','//*[@id="main-content"]/div/div/div/article/div/p[2]/text()')
        loader.add_xpath('application_method','//*[@id="main-content"]/div/div/div/article/div/section/p/text()')

        yield loader.load_item()
