# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# pipelines.py

from itemadapter import ItemAdapter
import sqlite3
from itemadapter import ItemAdapter
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os

class JobpostingscraperPipeline:
    """Cleaning of data not captured by the itemloader"""
    def process_item(self, item, spider):
        for key, value in item.items():
            if isinstance(value, list):
                item[key] = [val.strip() for val in value if val.strip()]
            elif isinstance(value, str):
                item[key] = value.strip()
        return item


class SQLDatabaseStoragePipeline:
    """Pipeline to store the items in a sqlite database"""
    
    def open_spider(self, spider):
        self.conn = sqlite3.connect("scraper_database.db")
        self.cur = self.conn.cursor()
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS job_postings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

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

            -- constraint preventing duplicate job postings
            CONSTRAINT unique_job_post UNIQUE (posted_by, title)
        );
        """)

        self.cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_company ON job_postings(posted_by);
        """)

    def process_item(self, item, spider):
        # skip items missing required fields
        if not item.get("title") or not item.get("posted_by"):
            spider.logger.warning(f"Skipping item missing title or posted_by: {item}")
            return item

        # convert lists to comma-separated strings if needed
        for key in ["minimum_requirements", "responsibilities"]:
            value = item.get(key)
            if isinstance(value, list):
                item[key] = ", ".join(value)

        try:
            self.cur.execute("""
                INSERT INTO job_postings (
                    title, field, posted_by, company, url,
                    date_posted, application_deadline,
                    minimum_requirements, responsibilities,
                    payment, type, application_method, location
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
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

            self.conn.commit()

        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            spider.logger.warning(f"Duplicate or constraint violation: {e}")

        except sqlite3.DatabaseError as e:
            self.conn.rollback()
            spider.logger.error(f"Database error: {e}")

        except Exception as e:
            self.conn.rollback()
            spider.logger.error(f"Unexpected error: {e}")

        return item

    def close_spider(self, spider):
        self.conn.close()


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

            -- constraint preventing duplicate job postings
            CONSTRAINT unique_job_post UNIQUE (posted_by, title)
        );
        """)

        self.cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_company ON job_postings(posted_by);
        """)

        self.conn.commit()

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
            self.cur.execute("""
                INSERT INTO job_postings (
                    title, field, posted_by, company, url,
                    date_posted, application_deadline,
                    minimum_requirements, responsibilities,
                    payment, type, application_method, location
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (posted_by, title) DO NOTHING;
            """, (
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

            self.conn.commit()

        except psycopg2.Error as e:
            self.conn.rollback()
            spider.logger.error(f"PostgreSQL insertion error: {e}")

        except Exception as e:
            self.conn.rollback()
            spider.logger.error(f"Unexpected error: {e}")

        return item

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()