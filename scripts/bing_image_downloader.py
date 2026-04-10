import argparse
import mimetypes
import os
from pathlib import Path
from urllib.parse import urlparse

import requests

from image_downloader.sources.bing import BingSource, HEADERS, extract_image_urls
from image_downloader.sources.demo import DemoSource


SOURCE_REGISTRY = {
    "bing": BingSource,
    "demo": DemoSource,
}


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


def build_sources(source_names):
    return [SOURCE_REGISTRY[name]() for name in source_names]


def collect_candidates_from_sources(keyword, limit, pages, sources):
    candidates = []
    for source in sources:
        candidates.extend(source.collect(keyword, limit=limit, pages=pages))
    return candidates


def collect_image_urls(keyword, pages=1, target_count=None):
    source = BingSource()
    limit = target_count if target_count is not None else pages * 35
    candidates = source.collect(keyword, limit=limit, pages=pages)
    return [candidate.image_url for candidate in candidates]


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
