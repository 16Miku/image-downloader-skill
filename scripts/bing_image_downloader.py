import argparse
import html
import json
import mimetypes
import os
import re
from pathlib import Path
from urllib.parse import quote, urlparse

import requests


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def extract_image_urls(html_text):
    patterns = [
        r'm=\'(\{.*?\})\'',
        r'm="(\{.*?\})"',
    ]

    seen = set()
    urls = []

    for pattern in patterns:
        matches = re.findall(pattern, html_text)
        for raw in matches:
            try:
                data = json.loads(html.unescape(raw))
            except json.JSONDecodeError:
                continue
            url = data.get("murl")
            if url and url not in seen:
                seen.add(url)
                urls.append(url)
    return urls


def guess_extension(url, content_type=None):
    if content_type:
        extension = mimetypes.guess_extension(content_type.split(";")[0].strip())
        if extension == ".jpe":
            return ".jpg"
        if extension:
            return extension

    path = urlparse(url).path.lower()
    for ext in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"):
        if path.endswith(ext):
            return ".jpg" if ext == ".jpeg" else ext
    return ".jpg"


def download_images(urls, output_dir, limit=10, start_index=1):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    saved_files = []

    for offset, url in enumerate(urls[:limit]):
        response = requests.get(url, headers=HEADERS, stream=True, timeout=15)
        response.raise_for_status()
        extension = guess_extension(url, response.headers.get("Content-Type"))
        filename = f"{start_index + offset:03d}{extension}"
        file_path = os.path.join(output_dir, filename)

        with open(file_path, "wb") as file_obj:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file_obj.write(chunk)

        saved_files.append(file_path)

    return saved_files


def collect_image_urls(keyword, pages=1, target_count=None):
    all_urls = []
    seen = set()

    for page in range(pages):
        if target_count is not None and len(all_urls) >= target_count:
            break

        first = page * 35 + 1
        url = f"https://www.bing.com/images/search?q={quote(keyword)}&form=HDRSC3&first={first}"
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        for image_url in extract_image_urls(response.text):
            if image_url not in seen:
                seen.add(image_url)
                all_urls.append(image_url)
                if target_count is not None and len(all_urls) >= target_count:
                    break

    return all_urls


def search_bing_images(keyword):
    return collect_image_urls(keyword, pages=1)


def main():
    parser = argparse.ArgumentParser(description="按关键词从 Bing 公开图片中下载图片")
    parser.add_argument("keyword", help="搜索关键词，例如 cat")
    parser.add_argument("--limit", type=int, default=10, help="下载数量，默认 10")
    parser.add_argument("--pages", type=int, default=5, help="最多抓取的 Bing 结果页数，默认 5")
    args = parser.parse_args()

    output_dir = os.path.join("downloads", args.keyword)
    image_urls = collect_image_urls(args.keyword, pages=args.pages, target_count=args.limit * 3)

    if not image_urls:
        print("没有提取到图片链接，请更换关键词后重试。")
        return

    success = 0
    for url in image_urls:
        if success >= args.limit:
            break
        try:
            saved = download_images([url], output_dir, limit=1, start_index=success + 1)
            if saved:
                success += 1
                print(f"下载成功: {saved[0]}")
        except Exception as exc:
            print(f"下载失败: {url} -> {exc}")

    print(f"共收集到 {len(image_urls)} 个候选链接。")
    print(f"完成，共成功下载 {success} 张图片。")


if __name__ == "__main__":
    main()
