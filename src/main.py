from jobs import create_crawl_job
from jobs import extract_image_urls
from datetime import datetime, timedelta


def main():
    job = create_crawl_job("BMW")
    extract_image_urls(job["id"])


if __name__ == "__main__":
    main()
