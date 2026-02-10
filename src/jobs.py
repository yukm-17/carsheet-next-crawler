from datetime import datetime, timedelta
import hashlib
import html
import json
from supabase_client import supabase
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests


# 크롤링 작업 단위 저장
def create_crawl_job(source_site: str):
    result = supabase.table("crawl_jobs").insert({
        "source_site": source_site,
        "status": "running",
    }).execute()

    return result.data[0]

# 차량 데이터 생성
def create_vehicle(card, crawl_job_id:str):
    element = card.select_one("[data-tracking-attributes]")

    if element:
        data = element.get("data-tracking-attributes")
        raw = {}

        if data:
            raw = json.loads(html.unescape(data))

        if raw:
            external_id = raw.get("productID")
            payload = {
                "crawl_job_id": crawl_job_id,
                "source_site": "BMW",
                "brand": "BMW",
                "model": raw.get("name"),
                "series": raw.get("series"),
                "fuel_type": raw.get("fuelType"),
                "body_type": raw.get("bodyType"),
                "external_id": external_id,
                "tracking_raw_json": raw,
            }

            res = supabase.table("vechicle_common").upsert(
                payload,
                on_conflict="source_site,external_id"
            ).execute()

            return res.data[0]

# 이미지 경로 수정(base url + 상대 경로 = 절대 경로)
def extract_image_urls(crawl_job_id: str) -> list[str]:
    url = "https://www.bmw.co.kr/ko/all-models.html?category=cp,li,comp,caro,to,suv"
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    for card in soup.select(".allmodelscard"):
        vehicle = create_vehicle(card, crawl_job_id)

        if not vehicle:
            continue

        image_urls = []
        imgs = card.select(".cmp-allmodelscarddetail__car-image img")

        for img in imgs:
            src = img.get("src") or img.get("data-src")
            if src:
                image_urls.append(urljoin(url, src))

        # 중복 제거(순서 유지)
        image_urls = list[str](dict.fromkeys(image_urls))

        if not image_urls:
            continue

        insert_images(vehicle["id"], image_urls, crawl_job_id)

# 이미지 insert
def insert_images(vehicle_id: str, image_urls: list[str], crawl_job_id: str):
    rows = []

    for url in image_urls:
        rows.append({
            "vehicle_id": vehicle_id,
            "image_url": url,
            "source_site": "BMW",
            "crawl_job_id": crawl_job_id,
            "image_hash": hashlib.sha256(url.encode()).hexdigest(),
        })

    supabase.table("images").upsert(rows, on_conflict="image_hash").execute()