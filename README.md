# Job Posting Scraper

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Scrapy](https://img.shields.io/badge/Scrapy-Web_Scraping-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue.svg)
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)

A **robust and concurrent web scraping framework** for collecting job postings from multiple job boards.  
This scraper normalizes and cleans data, extracts relevant information, and saves it into a PostgreSQL database. It supports multiple user-agent rotation for stealth crawling and concurrent crawling using a bash orchestration script.

---

## Features

### Data Extraction & Cleaning
- Extracts job postings using **Scrapy**.
- Uses **ItemLoaders** with processors: `TakeFirst`, `MapCompose`, `Join`, `Identity`.
- Cleans HTML and text using **w3lib.html**.
- Normalizes timestamps for all scraped entries.
- Uses **RapidFuzz** for fuzzy matching and parsing similar data points.

### Pipelines
- **Data Cleaning Pipeline** – further normalizes and validates scraped data.
- **Database Pipeline** – stores cleaned data in **PostgreSQL**.

### Concurrency & Job Persistence
- Uses **`job-dirs`** to save progress for each crawl.
- Bash script (`automated.sh`) manages **concurrent crawling** across multiple spiders.

### User-Agent Management
- Supports multiple user-agent rotation.
- Integrates **scrapy-fake-useragent** for randomized user-agent requests.
- Custom middleware handles dynamic UA rotation for all requests.

---

## Technology Stack

### Backend & Scraping
- **Python 3.11+**
- **Scrapy**
- **PostgreSQL**
- **RapidFuzz**
- **w3lib**
- **ItemLoaders**

### Utilities
- Bash scripting for concurrent spider execution.

---

## System Architecture
      ┌───────────────┐
      │   Scrapy      │
      │   Spiders     │
      └──────┬────────┘
             │
             ▼
      ┌───────────────┐
      │ ItemLoaders   │
      │ - Normalize   │
      │ - Clean HTML  │
      │ - RapidFuzz   │
      └──────┬────────┘
             │
             ▼
      ┌───────────────┐
      │  Pipelines     │
      │ - Data Clean   │
      │ - PostgreSQL   │
      └──────┬────────┘
             │
             ▼
      ┌───────────────┐
      │ Job Dirs /    │
      │ Progress Save │
      └──────┬────────┘
             │
             ▼
      ┌───────────────┐
      │ Bash Script   │
      │ Concurrent    │
      │ Crawling      │
      └───────────────┘



---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/job-posting-scraper.git
cd job-posting-scraper
```

### 2. Create a virtual environment
```bash
python -m venv venv
```

Activate it:

#### Linux / Mac
```bash
source venv/bin/activate
```

#### Windows
```bash
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a .env file:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/jobs_db
REDIS_URL=redis://localhost:6379
```

### 5. Run the scraper

To execute all spiders concurrently:

```bash
bash automated.sh
```

Individual spiders can also be run using Scrapy:
```bash
scrapy crawl <spider_name>
```

### Project Structure
```bash
├── automated.sh
├── crawls/
├── JobPostingScraper/
│   ├── __init__.py   
│   ├── itemloader.py 
│   ├── items.py      
│   ├── middlewares.py
│   ├── pipelines.py  
│   ├── settings.py
│   └── spiders/
├── LICENSE
├── README.md
├── requirements.txt
└── scrapy.cfg
```

### Key Libraries
| Library               | Purpose                                  |
| --------------------- | ---------------------------------------- |
| Scrapy                | Main web scraping framework              |
| ItemLoaders           | Normalize and clean scraped items        |
| w3lib                 | HTML cleaning and parsing                |
| RapidFuzz             | Fuzzy string matching for similar fields |
| PostgreSQL            | Storage of scraped job data              |
| scrapy-fake-useragent | Rotate User Agents                       |

### Data Handling

* Job directories save crawl progress.

* Normalized timestamps ensure consistency across all records.

* Data cleaning pipelines remove inconsistencies before database insertion.

# License

This project is licensed under the **GPL- 3.0 license**.

---

# Author

- Developed as a robust multi-site scraper for job market data collection, supporting clean, normalized, and structured storage of job postings for analytics and further processing.
---