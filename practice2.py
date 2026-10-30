import csv
import time
from urllib.parse import urljoin, urlparse, urlunparse
import requests
from bs4 import BeautifulSoup

START_URLS = [
    "https://www.musashino-u.ac.jp/",
    "https://www.musashino-u.ac.jp/sitemap/",
]
TARGET_DOMAIN = "www.musashino-u.ac.jp"
OUTPUT_FILE = "musashino_u_sitemap.csv"
WAIT_TIME = 0.5

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

SKIP_EXTENSIONS = (
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg",
    ".zip", ".docx", ".xlsx", ".pptx", ".css", ".js", ".ico"
)

def normalize_url(url):
    parsed = urlparse(url)
    if any(parsed.path.lower().endswith(ext) for ext in SKIP_EXTENSIONS):
        return None
    
    path = parsed.path
    if path and not path.endswith('/'):
        if not any(path.endswith(ext) for ext in SKIP_EXTENSIONS):
            path += '/'

    return urlunparse((
        parsed.scheme,
        parsed.netloc.lower(),
        path,
        parsed.params,
        parsed.query,
        ""
    ))

def get_page_info(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            return None, []

        response.raise_for_status()
        response.encoding = response.apparent_encoding

        soup = BeautifulSoup(response.text, "html.parser")

        if not soup.title or not soup.title.string or not soup.title.string.strip():
            return None, []

        title = soup.title.string.strip()

        links = []
        for a_tag in soup.find_all("a", href=True):
            full_url = urljoin(url, a_tag["href"])
            norm_url = normalize_url(full_url)

            if norm_url:
                parsed_link = urlparse(norm_url)
                if parsed_link.netloc == TARGET_DOMAIN and parsed_link.scheme in ("http", "https"):
                    links.append(norm_url)

        return title, links

    except requests.exceptions.RequestException:
        return None, []

def run_crawler():
    visited_urls = set()
    urls_to_visit = []
    
    for start_url in START_URLS:
        norm_start = normalize_url(start_url)
        if norm_start:
            urls_to_visit.append(norm_start)

    sitemap_data = {}

    # ファイルを新規作成（ヘッダーの書き込み）
    with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["URL", "Title"])

    print("--- 巡回を開始します（1件ごとに即時書き込み保存） ---")

    try:
        while urls_to_visit:
            current_url = urls_to_visit.pop(0)

            if current_url in visited_urls:
                continue

            visited_urls.add(current_url)

            title, links = get_page_info(current_url)

            if title:
                sitemap_data[current_url] = title

                # 取得するたびにCSVへ追記（aモード）する
                with open(OUTPUT_FILE, mode="a", newline="", encoding="utf-8-sig") as file:
                    writer = csv.writer(file)
                    writer.writerow([current_url, title])

                print(f"[{len(sitemap_data)}件保存] 取得: {current_url} | 残りキュー: {len(urls_to_visit)}件")

                for link in links:
                    if link not in visited_urls and link not in urls_to_visit:
                        urls_to_visit.append(link)

                time.sleep(WAIT_TIME)

    except KeyboardInterrupt:
        print("\n手動で停止されました。")
    except Exception as e:
        print(f"\nエラーまたは通信切断が発生しました: {e}")
    finally:
        print(f"\n終了時点の保存件数: {len(sitemap_data)} 件が '{OUTPUT_FILE}' に保存されています。")

if __name__ == "__main__":
    run_crawler()