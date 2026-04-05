import scrapy
from JobPostingScraper.items import JobpostingscraperItem
from JobPostingScraper.itemloader import JobLoader

class BrightermondaySpider(scrapy.Spider):
    name = "brighterMonday"
    allowed_domains = ["www.brightermonday.co.ke"]
    start_urls = [
                    "https://www.brightermonday.co.ke/jobs",
                    'https://www.brightermonday.co.ke/jobs/advertising-media-communications',
                    'https://www.brightermonday.co.ke/jobs/agriculture-fishing-forestry',    
                    'https://www.brightermonday.co.ke/jobs/automotive-aviation',
                    'https://www.brightermonday.co.ke/jobs/banking-finance-insurance',       
                    'https://www.brightermonday.co.ke/jobs/construction',
                    'https://www.brightermonday.co.ke/jobs/education',
                    'https://www.brightermonday.co.ke/jobs/energy-utilities',
                    'https://www.brightermonday.co.ke/jobs/enforcement-security',
                    'https://www.brightermonday.co.ke/jobs/entertainment-events-sport',      
                    'https://www.brightermonday.co.ke/jobs/government',
                    'https://www.brightermonday.co.ke/jobs/healthcare',
                    'https://www.brightermonday.co.ke/jobs/hospitality-hotel',
                    'https://www.brightermonday.co.ke/jobs/it-telecoms',
                    'https://www.brightermonday.co.ke/jobs/law-compliance',
                    'https://www.brightermonday.co.ke/jobs/manufacturing-warehousing',       
                    'https://www.brightermonday.co.ke/jobs/mining-energy-metals',
                    'https://www.brightermonday.co.ke/jobs/ngo-npo-charity',
                    'https://www.brightermonday.co.ke/jobs/real-estate',
                    'https://www.brightermonday.co.ke/jobs/recruitment',
                    'https://www.brightermonday.co.ke/jobs/retail-fashion-fmcg',
                    'https://www.brightermonday.co.ke/jobs/shipping-logistics',
                    'https://www.brightermonday.co.ke/jobs/tourism-travel'
                ]

    def __init__(self):
        self.next_page = 2

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, meta={"page": 1, "base_url": url})

    def parse(self, response):
        # vertical crawling
        links =  response.xpath('/html/body/main/section/div[3]/div[2]/div[1]/div/div/div/div/div/a/@href').getall()
        for link in links:
            yield response.follow(link,callback=self.parse_job)

        # horixontal crawling
        try:
            page = response.meta["page"]
            base_url = response.meta["base_url"]
            page_links = response.xpath('/html/body/main/section/div[3]/div[2]/div[1]/nav/div/span/a/@href').getall()
            next_url = f"{base_url}?page={page + 1}"
            # print(f"Next url = {next_url}")

            if next_url in page_links:
                # print(f"Crawling to url: {next_url}")
                # print(f"Current page: {page}")

                yield response.follow(
                    next_url,
                    callback=self.parse,
                    meta={"page": page + 1, "base_url": base_url}
                )
        except Exception as e:
            print(f"Error: {str(e)}")
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
