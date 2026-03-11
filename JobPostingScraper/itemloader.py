from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst,MapCompose,Join,Identity
import w3lib.html
from datetime import datetime
from rapidfuzz import process


def parse_date(value):
    value = value.strip()
    for fmt in ("%B %d, %Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None 


def parse_job_type(value:str):
    try:
        value = value.strip()
        options = ["Remote","Full Time","Part Time","Contract","Freelance","Shift Work","Rotational","Flexible Hours","Hybrid","Casual",""]

        best_match = process.extractOne(value,options)

        return best_match[0]
    except:
        return value



class JobLoader(ItemLoader):
    default_output_processor = TakeFirst()

    # basic info
    title_in = MapCompose(w3lib.html.remove_tags,str.strip)
    field_in = MapCompose(str.strip,w3lib.html.remove_tags)
    field_out = Join(", ")
    posted_by_in = MapCompose(w3lib.html.remove_tags,str.strip)
    company_in = MapCompose(w3lib.html.remove_tags,str.strip)
    url_in = MapCompose(str.strip)

    # dates
    date_posted_in = MapCompose(str.strip,w3lib.html.remove_tags,parse_date)
    application_deadline_in = MapCompose(str.strip,w3lib.html.remove_tags,parse_date)

    # other details
    minimum_requirements_in = MapCompose(str.strip,w3lib.html.remove_tags)
    minimum_requirements_out = Identity()
    responsibilities_in = MapCompose(str.strip,w3lib.html.remove_tags)
    responsibilities_out = Identity()
    payment_in = MapCompose(str.strip,w3lib.html.remove_tags)
    type_in = MapCompose(str.strip,w3lib.html.remove_tags,parse_job_type) # like contract,intern etc
    application_method_in = MapCompose(w3lib.html.remove_tags)
    application_method_out = Join(", ")
    location = MapCompose(str.strip,w3lib.html.remove_tags)

