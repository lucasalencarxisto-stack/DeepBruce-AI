# Coletor mínimo da Wikipédia usando REST API, com fallback em HTML.
from typing import Dict
import requests
from bs4 import BeautifulSoup
import time

BASE = "https://{lang}.wikipedia.org/api/rest_v1"
HEADERS = {"User-Agent": "OQS_step3/1.0 (contact: local)"}

def _get(url: str, tries: int = 3):
    for i in range(tries):
        r = requests.get(url, timeout=30, headers=HEADERS)
        if r.status_code == 200:
            return r
        if r.status_code in (429, 503):
            time.sleep(1.0 + i * 0.5)
            continue
        break
    return None

def _plain(lang: str, title: str) -> Dict:
    r = _get(f"{BASE.format(lang=lang)}/page/plain/{title}")
    if r and r.status_code == 200:
        return {"title": title.replace("_"," "), "text": r.text, "url": f"https://{lang}.wikipedia.org/wiki/{title}"}
    return {}

def _html(lang: str, title: str) -> Dict:
    r = _get(f"{BASE.format(lang=lang)}/page/html/{title}")
    if not r or r.status_code != 200:
        return {}
    soup = BeautifulSoup(r.text, "html.parser")
    for el in soup.select("table, .reference, sup.reference"):
        el.decompose()
    text = soup.get_text(" ")
    return {"title": title.replace("_"," "), "text": text, "url": f"https://{lang}.wikipedia.org/wiki/{title}"}

def fetch_wikipedia_page(title: str, lang: str = "pt") -> Dict:
    title = title.strip().replace(" ", "_")
    data = _plain(lang, title)
    if data.get("text"):
        return data
    return _html(lang, title)

