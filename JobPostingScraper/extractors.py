import spacy
from sqlalchemy import create_engine,select,MetaData,Table,update,or_,func
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
from datetime import datetime
import threading

NLP = spacy.load("en_core_web_lg")
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL,echo=False)
Base = declarative_base()
metadata = MetaData()

job_table = Table("job_postings",metadata,autoload_with=engine)


class LocationExtractor:
    '''Extracts location from text and saves to the db'''

    def __init__(self):
        pass
    
    def fetch_db_data(self):
        # some data have long locations names which is not ideal so we fetch the location as well and filter it out
        query = select(
            job_table.c.title,
            job_table.c.location,
            job_table.c.id
        ).where(
            or_(
                job_table.c.location.is_(None),
                func.length(job_table.c.location) > 50
            )
        )

        with engine.connect() as conn:
            results = conn.execute(query).mappings().all()
            return [(str(row["title"]) + str(row["location"]),row["id"]) for row in results]
        
    def extract_location(self,text):
        doc = NLP(text)
        locations = []
        for ent in doc.ents:
            if ent.label_ in ["GPE","LOC"]:
                locations.append(ent.text)
        
        if locations:
            return ", ".join(locations)
        else:
            return None
    
    def update_table(self,data:tuple):
        stmt = (
            update(job_table)
            .where(job_table.c.id==data[1])
            .values(location=data[2])
        )

        with engine.connect() as conn:
            conn.execute(stmt)

class CompanyExtractor:
    '''Extracts company from text and saves to db'''

    def __init__(self):
        pass
    
    def fetch_titles_db(self):
        query = select(job_table.c.title).where(job_table.c.company.is_(None))

        with engine.connect() as conn:
            results = conn.execute(query).mappings().all()
            return [row["title"] for row in results]
        
    def extract_company(self,text):
        doc = NLP(text)
        companies = []
        for ent in doc.ents:
            if ent.label_ == "ORG":
                companies.append(ent.text)
        
        if companies:
            return ", ".join(companies)
        else:
            return None

    def update_table(self,data:tuple):
        stmt = (
            update(job_table)
            .where(job_table.c.title==data[0])
            .values(company=data[1])
        )

        with engine.connect() as conn:
            conn.execute(stmt)
    

def company_pipeline():
    comp_obj = CompanyExtractor()
    titles = comp_obj.fetch_titles_db()
    for title in titles:
        print(f'[Company extractor] ---{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} ---{title}...')
        company = comp_obj.extract_company(title)
        if company:
            print(f"[+] Found the company...{company}")
            db_data = (title,company)
            comp_obj.update_table(db_data)
        else:
            continue


def location_pipeline():
    loc_obj = LocationExtractor()
    data = loc_obj.fetch_db_data()
    for item in data:
        print(f'[Location extractor] ---{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} ---{item[0]}...')
        location = loc_obj.extract_location(item[0])
        if location:
            print(f"[+] Found the location...{location}")
            db_data = (item[0],item[1],location)
            loc_obj.update_table(db_data)
        else:
            continue


if __name__ == "__main__":
    # running both pipelines in parallel since they are independent of each other and it will save time
    t1 = threading.Thread(target=company_pipeline)
    t2 = threading.Thread(target=location_pipeline)
    t1.start()
    t2.start()
    t1.join()
    t2.join()