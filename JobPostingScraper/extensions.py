# extensions.py
import json
from scrapy import signals
from datetime import datetime
import logging


class SaveStatsExtension:
    def __init__(self, stats):
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls(crawler.stats)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        return ext

    def spider_closed(self, spider):
        stats_dict = self.stats.get_stats()
        stats_dict["spider_name"] = spider.name
        stats_dict["closed_at"] = datetime.now().isoformat()

        with open("scrapy_stats.json", "a") as f:
            json.dump(stats_dict, f, default=str, indent=4)
            f.write("\n---\n")  # separator between spider entries



class FileAndConsoleLogging:
    @classmethod
    def from_crawler(cls, crawler):
        ext = cls()
        
        fmt = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
        
        # file handler — WARNING and above only
        fh = logging.FileHandler("jobscraper.log", encoding="utf-8")
        fh.setLevel(logging.WARNING)
        fh.setFormatter(fmt)

        # console handler — INFO and above
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(fmt)

        root = logging.getLogger()
        root.addHandler(fh)
        root.addHandler(ch)

        return ext