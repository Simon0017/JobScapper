# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobpostingscraperItem(scrapy.Item):
    # basic info
    title = scrapy.Field()
    field = scrapy.Field()
    posted_by = scrapy.Field() # ad company
    company  = scrapy.Field()
    url = scrapy.Field()

    # dates
    date_posted = scrapy.Field()
    application_deadline = scrapy.Field()

    # other details
    minimum_requirements = scrapy.Field()
    responsibilities = scrapy.Field()
    payment = scrapy.Field()
    type = scrapy.Field()
    application_method = scrapy.Field()
    location = scrapy.Field()


