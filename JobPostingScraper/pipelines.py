# pipelines.py
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os
import datefinder
from datetime import datetime, timedelta
from scrapy.exceptions import DropItem
from rapidfuzz import fuzz

class JobpostingscraperPipeline:
    """Cleaning of data not captured by the itemloader"""
    def process_item(self, item, spider):
        for key, value in item.items():
            if isinstance(value, list):
                item[key] = [val.strip() for val in value if val.strip()]
            elif isinstance(value, str):
                item[key] = value.strip()
        
        # removing old-dated postings/expired
        application_deadline = str(item.get("application_deadline","")).strip().lower()

        # 1. explicit expired keyword
        threshold = 90
        if fuzz.partial_ratio("expired", application_deadline) > threshold:
            spider.logger.info(f"[DROP] expired | source={item.get('posted_by')} | deadline={application_deadline}")
            raise DropItem("Job posting expired")

        # 2. extract dates
        if len(application_deadline) < 6:   # too short to be a real date string
            pass  # skip parsing
        else:
            date_matches = list(datefinder.find_dates(
                application_deadline,
                strict=True
                ))
            if date_matches:
                deadline_parsed = max(date_matches).replace(tzinfo=None)
                if deadline_parsed < datetime.now():
                    spider.logger.info(f"[DROP] expired | source={item.get('posted_by')} | deadline={application_deadline}")
                    raise DropItem("Job posting expired")
        
        # 3 delete those that the date posted is passed
        date_posted = str(item.get("date_posted","")).strip().lower()
        if len(date_posted) < 6:
            pass
        else:
            date_matches = list(datefinder.find_dates(date_posted,strict=True))
            if date_matches:
                posted_parsed = max(date_matches).replace(tzinfo=None)
                if posted_parsed < datetime.now() - timedelta(days=45):
                    spider.logger.info(f"[DROP] Job posting too old | source={item.get('posted_by')} | date_posted={date_posted}")
                    raise DropItem("Job posting too old")

        return item


class PostgreSQLDatabasePipeline:
    """Pipeline to store the items in a PostgreSQL database"""

    def open_spider(self, spider):
        # Load env vars
        load_dotenv()
        self.conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD")
        )
        self.cur = self.conn.cursor()

        # Create table if not exists
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS job_postings (
            id SERIAL PRIMARY KEY,

            -- basic info
            title TEXT NOT NULL,
            field TEXT,
            posted_by TEXT NOT NULL,
            company TEXT,
            url TEXT UNIQUE,

            -- dates as TEXT
            date_posted TEXT,
            application_deadline TEXT,

            -- other details
            minimum_requirements TEXT,
            responsibilities TEXT,
            payment TEXT,
            type TEXT,
            application_method TEXT,
            location TEXT,
            crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            -- constraint preventing duplicate job postings
            CONSTRAINT unique_job_post UNIQUE (posted_by, title)
        );
        """)

        self.cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_company ON job_postings(posted_by);
        """)

        self.conn.commit()

        self.buffer = [] 
        self.BATCH_SIZE = 50  

    def process_item(self, item, spider):
        # Skip items with missing required fields
        if not item.get("title") or not item.get("posted_by"):
            spider.logger.warning(f"Skipping item missing title or posted_by: {item}")
            return item

        # Convert list fields to comma-separated string
        for key in ["minimum_requirements", "responsibilities"]:
            value = item.get(key)
            if isinstance(value, list):
                item[key] = ", ".join(value)

        try:
            self.buffer.append((
                item.get("title"),
                item.get("field"),
                item.get("posted_by"),
                item.get("company"),
                item.get("url"),
                str(item.get("date_posted")) if item.get("date_posted") else None,
                str(item.get("application_deadline")) if item.get("application_deadline") else None,
                item.get("minimum_requirements"),
                item.get("responsibilities"),
                item.get("payment"),
                item.get("type"),
                item.get("application_method"),
                item.get("location"),
            ))

            if len(self.buffer) >= self.BATCH_SIZE:
                self._flush()

        except psycopg2.Error as e:
            self.conn.rollback()
            spider.logger.error(f"PostgreSQL insertion error: {e}")

        except Exception as e:
            self.conn.rollback()
            spider.logger.error(f"Unexpected error: {e}")

        return item
    

    def _flush(self):
        if not self.buffer:
            return


        try:
            execute_values(self.cur, """
                INSERT INTO job_postings (
                    title, field, posted_by, company, url,
                    date_posted, application_deadline,
                    minimum_requirements, responsibilities,
                    payment, type, application_method, location
                ) VALUES %s
                ON CONFLICT (posted_by, title) DO NOTHING
            """, self.buffer)
            self.conn.commit()
            self.buffer.clear()
        except psycopg2.Error as e:
            self.conn.rollback()
            self.buffer.clear()   # ← not retrying poison data endlessly
            raise                 # ← Scrapy log it properly

    def close_spider(self, spider):
        try:
            self._flush()
        except Exception as e:
            spider.logger.error(f"Final flush failed: {e}")
        finally:
            self.cur.close() 
            self.conn.close()   
