#!/bin/bash

echo "Starting brighterMonday..."
scrapy crawl brighterMonday -s JOBDIR=crawls/brighterMonday &

echo "Starting CorporateStaffing..."
scrapy crawl CorporateStaffing -s JOBDIR=crawls/CorporateStaffing &

echo "Starting MyJobMag..."
scrapy crawl MyJobMag -s JOBDIR=crawls/MyJobMag &

echo "Starting summitRecruitment..."
scrapy crawl summitRecruitment -s JOBDIR=crawls/summitRecruitment &

# Wait for all background jobs to finish
wait

echo "All spiders finished!"