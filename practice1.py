import requests
from bs4 import BeautifulSoup
import csv
import time
from urllib.parse import urljoin, urlparse

# 設定
START_URL = "https://www.musashino-u.ac.jp/"  # 武蔵野大学のトップページ
# START_URL = "https://www.musashino-u.ac.jp/sitemap/" # サイトマップページから始める場合
DOMAIN = urlparse(START_URL).netloc
OUTPUT_FILE = "musashino_u_sitemap.csv"
WAIT_TIME = 2  # アクセス間の待機時間（秒）

def get_page_info(url):
    """
    指定されたURLのページからタイトルとリンクを取得する
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # エラーがあれば例外を発生させる
        response.encoding = response.apparent_encoding  # 文字化け対策

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # タイトルの取得
        title = soup.title.string.strip() if soup.title else "No Title"
        
        # リンクの取得
        links = []
        for a_tag in soup.find_all('a', href=True):
            link = urljoin(url, a_tag['href'])
            # 同じドメインのリンクのみを追加（フラグメントを除く）
            parsed_link = urlparse(link)
            if parsed_link.netloc == DOMAIN:
                # URLを正規化（http/httpsの統一や、末尾のスラッシュの有無など）
                normalized_link = f"{parsed_link.scheme}://{parsed_link.netloc}{parsed_link.path}"
                links.append(normalized_link)
        
        return title, links

    except requests.exceptions.RequestException as e:
        print(f"Error accessing {url}: {e}")
        return None, []

def create_sitemap():
    # 訪問済みのURLを記録するセット
    visited_urls = set()
    # 訪問予定のURLを管理するキュー（リストをキューとして使用）
    urls_to_visit = [START_URL]
    # 結果を格納する辞書
    sitemap_data = {}

    while urls_to_visit:
        # キューから次のURLを取り出す
        current_url = urls_to_visit.pop(0)

        if current_url in visited_urls:
            continue

        print(f"Visiting: {current_url}")
        
        # ページ情報の取得
        title, links = get_page_info(current_url)
        
        if title is not None:
            # 取得できた場合は辞書に格納
            sitemap_data[current_url] = title
            visited_urls.add(current_url)

            # 新しいリンクを訪問予定リストに追加
            for link in links:
                if link not in visited_urls and link not in urls_to_visit:
                    urls_to_visit.append(link)

            # サーバー負荷軽減のための待機
            time.sleep(WAIT_TIME)

    return sitemap_data

def save_to_csv(data, filename):
    """
    取得したデータをCSVファイルに保存する
    """
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['URL', 'Title'])
        for url, title in data.items():
            writer.writerow([url, title])
    print(f"Sitemap saved to {filename}")

if __name__ == "__main__":
    print("Starting sitemap creation...")
    result_sitemap = create_sitemap()
    print("Sitemap creation finished.")
    
    if result_sitemap:
        save_to_csv(result_sitemap, OUTPUT_FILE)
    else:
        print("No data was retrieved.")