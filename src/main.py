from jobs import create_crawl_job
from jobs import extract_image_urls
from datetime import datetime, timedelta
import requests

def main():
    # job = create_crawl_job(source_site="bmw_official")
    # print("Crawl job created:", job["id"])

    url = "https://www.bmw.co.kr/ko/all-models.html?category=cp"
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    image_urls = extract_image_urls(res.text, url)

    print(image_urls)

if __name__ == "__main__":
    main()
