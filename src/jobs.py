from datetime import datetime, timedelta
from supabase_client import supabase
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def create_crawl_job(source_site: str):
    result = supabase.table("image_crawl_jobs").insert({
        "source_site": source_site,
        "status": "running",
    }).execute()

    return result.data[0]

def extract_image_urls(html: str, url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    image_urls = []

    for img in soup.select("img"):
        if img.get("src"):
            image_urls.append(img["src"])
        elif img.get("data-src"):
            image_urls.append(img["data-src"])

    normalized_urls = [
        urljoin(url, src)
        for src in image_urls
    ]
    normalized_urls = list(set(normalized_urls))

    return normalized_urls